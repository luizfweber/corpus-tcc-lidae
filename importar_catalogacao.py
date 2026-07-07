#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTOCOLO DE IMPORTAÇÃO E LIMPEZA de novas catalogações de TCCs (LIDAE/UFRR).

Uso:
    python3 importar_catalogacao.py "caminho/para/nova_catalogacao.csv"
    python3 importar_catalogacao.py "arquivo.csv" --aplicar     # grava de fato

Sem --aplicar, roda em modo SIMULAÇÃO (dry-run): mostra o relatório e não grava
nada. Com --aplicar, faz backup do consolidado e anexa as linhas novas.

O que este script faz (parte MECÂNICA, reproduzível):
  1. Detecta DUPLICATAS contra a base, por título normalizado (sem acento/caixa).
     Pula linhas cujo título é uma URL (campo preenchido errado).
  2. Mapeia curso -> grupo_tcc / curso_fonte (LEDUCAR -> LEDUCARR; cursos novos
     entram como novo grupo).
  3. Limpa a BANCA para o formato "Nome | Nome | Nome": remove títulos (Prof.,
     Dr., ...), funções (Orientador, Membro, ...), instituições (UFRR, Curso de
     ..., Universidade, ...), parênteses e resíduos ordinais (º, ª); corta
     vazamentos de "Palavras-chave".
  4. UNIFICA cada nome (banca e orientador) por fuzzy matching contra os nomes
     canônicos já existentes na base (resolve truncamentos, inversões e acentos).
  5. Gera banca_membro_1..4 (o ORIENTADOR é excluído; fica só na coluna
     orientador).
  6. Guarda de plausibilidade: ano fora de 1990-2030 vira ausente (não imputar).
  7. Imprime RELATÓRIO: novos por curso, duplicatas, e nomes que ainda merecem
     conferência manual (fuzzy no limiar, ou sem correspondência na base).

DEPOIS deste script (passos que exigem JULGAMENTO, feitos à parte):
  - python3 analise_corpus.py        (recalcula tópicos, clusters, menção indígena)
  - re-curar rótulos em TOPICOS (dashboard.py) a partir dos termos impressos
  - categorizar cursos novos em analise_por_curso.py (LDA/descritivo/listagem)
    e rodá-lo
  - validar (252==252, sem colunas .1, habilitações sem fallback, 0 residuos),
    reiniciar o dashboard e publicar
Ver PROTOCOLO_DADOS.md para o passo a passo completo.
"""
import sys, re, unicodedata, shutil, datetime
from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz, process

BASE = Path(__file__).parent
CONSOLIDADO = BASE / "outputs" / "corpus_tccs_consolidado.csv"
ANALISADO = BASE / "outputs" / "analise" / "corpus_tccs_analisado.csv"
BACKUPS = BASE / "outputs" / "backups"

LIMIAR_FUZZY = 90          # >= : unifica automaticamente com nome existente
LIMIAR_REVISAO = 82        # entre REVISAO e FUZZY: apenas sinaliza p/ conferência

# Mapa de curso -> grupo_tcc. Cursos ausentes aqui entram como grupo = próprio nome.
GRUPO = {
    "História": "História",
    "Ciências Biológicas": "Ciências Biológicas",
    "Pedagogia": "Pedagogia", "Música": "Música", "Matemática": "Matemática",
    "Insikiran – Ciências da Natureza": "Insikiran",
    "Insikiran – Ciências Sociais": "Insikiran",
    "Insikiran – Comunicação e Artes": "Insikiran",
    "LEDUCAR – Ciências Humanas e Sociais": "LEDUCARR",
    "LEDUCAR – Ciências da Natureza e Matemática": "LEDUCARR",
    "LEDUCARR – Ciências Humanas e Sociais": "LEDUCARR",
    "LEDUCARR – Ciências da Natureza e Matemática": "LEDUCARR",
    "Letras – Inglês": "Letras", "Letras – Português": "Letras",
    "Letras – Curso anterior": "Letras",
}

# Mapa de colunas do formulário -> colunas do consolidado.
FORM2COL = {
    "Carimbo de data/hora": "carimbo",
    "Pesquisador/a responsável pelo registro": "pesquisador",
    "Link ou localização do TCC": "link", "TCC digital?": "tcc_digital",
    "Formato do documento analisado": "formato",
    "TCC disponível integralmente?": "disponivel_integral",
    "Observações sobre acesso ao documento": "observacoes_acesso",
    "Título completo do TCC": "titulo", "Tipo do TCC": "tipo_tcc",
    "Autor/a do TCC": "autor", "Coorientador/a, se houver": "coorientador",
    "Ano de defesa": "ano_defesa", "Semestre de defesa, se houver": "semestre_defesa",
    "Número de páginas": "paginas", "Palavras-chave informadas no TCC": "palavras_chave",
    "Resumo disponível?": "resumo_disponivel", "Resumo do TCC": "resumo",
    "Observações da análise": "observacoes_analise", "Envio do arquivo do TCC": "arquivo",
}

# ── utilitários de normalização ──────────────────────────────────────────────
def fold(s):
    s = str(s or "").lower().strip()
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s)

def keyf(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s).lower())
                   if not unicodedata.combining(c)).strip()

_CONN = {"de", "da", "do", "dos", "das", "e"}
def tcase(s):
    return " ".join(w if w.lower() in _CONN else (w[:1].upper() + w[1:].lower())
                    for w in s.split())

_TIT = re.compile(r"\b(Prof(?:essor)?[ao]?|Dr[ao]?|Drª|Doutor[a]?|Me|Msc|Ms|"
                  r"Mestre|Esp|MSc|Ma|Mst|Mr)\b\.?", re.I)
_INST = re.compile(r"\s*(?:Curso\s+de|Curso\b|Universidade|Instituto|Licenciatura|"
                   r"Departamento|Centro|UFRR|UERR|IFRR|IFPA|SEED|CEDUC|"
                   r"Educação\s+do\s+Campo)\b", re.I)
_INSTKW = ("curso", "licenciatura", "universidade", "instituto", "departamento",
           "ufrr", "uerr", "ifrr", "ifpa", "seed", "ceduc", "educacao do campo")
_ROLE = re.compile(r"^(presidente|membro|orientador|banca|curso)\b", re.I)
_NAO = re.compile(r"^\s*n[ãa]o\b", re.I)

def _base_clean(p):
    """Remove título, instituição, função, parênteses e resíduos de um trecho."""
    p = str(p)
    # ordinais colados aos títulos (Profº, Drª) viram espaço ANTES do strip de
    # título, senão 'Profº' não casa \bProf\b e o título sobrevive.
    p = p.replace("º", " ").replace("ª", " ")
    p = re.split(r"(?:palavras?[\s-]*chave)", p, flags=re.I)[0]
    p = re.split(r"\s*[:\-–]\s*(orientador|membro|presidente|titular|suplente|"
                 r"coorientador|curso)", p, flags=re.I)[0]
    p = re.sub(r"\([^)]*\)", "", p)
    p = re.sub(r"\(.*$", "", p)
    p = _INST.split(p)[0]
    p = _TIT.sub("", p)
    p = p.replace(".", " ")
    p = re.sub(r"[^\w\s'’]", " ", p)
    p = re.sub(r"\b[ºªao]\b", "", p)           # resíduos ª/º/a/o soltos
    return tcase(re.sub(r"\s+", " ", p).strip())


class Unificador:
    """Casa nomes limpos contra o conjunto canônico já existente na base."""
    def __init__(self, base):
        canon = set()
        for c in ["orientador", "banca_membro_1", "banca_membro_2",
                  "banca_membro_3", "banca_membro_4"]:
            if c in base.columns:
                canon |= {str(x).strip() for x in base[c].dropna()
                          if str(x).strip() not in ("", "nan")}
        canon.discard("Não informado")
        self.key2nome = {keyf(x): x for x in sorted(canon)}
        self.chaves = list(self.key2nome)
        self.revisar = []      # (nome_novo, melhor_match, score)

    def unifica(self, nm):
        if not nm or _ROLE.match(nm):
            return None
        low = keyf(nm)
        if any(w in low for w in _INSTKW):
            return None
        if low in self.key2nome:
            return self.key2nome[low]
        m = process.extractOne(low, self.chaves, scorer=fuzz.token_sort_ratio)
        if m and m[1] >= LIMIAR_FUZZY:
            return self.key2nome[m[0]]
        if m and m[1] >= LIMIAR_REVISAO:
            self.revisar.append((nm, self.key2nome[m[0]], round(m[1])))
        return nm      # nome novo (mantém como está)

    def clean_banca(self, v):
        if pd.isna(v) or str(v).strip() == "" or _NAO.match(str(v).strip()):
            return ""
        out, seen = [], set()
        for p in re.split(r"[;\n]| e (?=[A-ZÁÉ])", str(v)):
            nm = self.unifica(_base_clean(re.sub(r"^\s*e\s+", "", p)))
            if not nm or len(nm.split()) < 2 or len(nm) <= 5:
                continue
            if keyf(nm) not in seen:
                seen.add(keyf(nm)); out.append(nm)
        return " | ".join(out)

    def clean_orient(self, v):
        if pd.isna(v) or str(v).strip() == "":
            return "Não informado"
        base = re.split(r"\s+(orientador|orientadora)\b", str(v), flags=re.I)[0]
        return self.unifica(_base_clean(base)) or "Não informado"


def ano_plausivel(v):
    try:
        a = float(str(v).strip().replace(",", "."))
    except Exception:
        return v
    return v if 1990 <= a <= 2030 else ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    aplicar = "--aplicar" in sys.argv
    if not args:
        print(__doc__); sys.exit(1)
    novo_path = args[0]

    novo = pd.read_csv(novo_path)
    con = pd.read_csv(CONSOLIDADO)
    print(f"Base atual: {len(con)} TCCs | Arquivo novo: {len(novo)} linhas")

    # 1. duplicatas
    base_titulos = set(con["titulo"].apply(fold))
    novo["_f"] = novo["Título completo do TCC"].apply(fold)
    novo["_url"] = novo["Título completo do TCC"].astype(str).str.startswith("http")
    ja = novo[novo["_f"].isin(base_titulos) & ~novo["_url"]]
    url = novo[novo["_url"]]
    novos = novo[~novo["_f"].isin(base_titulos) & ~novo["_url"]].copy()
    print(f"\n== DUPLICATAS / FILTRO ==")
    print(f"  Já cadastrados (ignorados): {len(ja)}")
    print(f"  Título é URL (pulados):     {len(url)}")
    print(f"  NOVOS a inserir:            {len(novos)}")
    if novos.empty:
        print("\nNada novo a importar."); return

    print(f"\n== NOVOS POR CURSO ==")
    print(novos["Curso/licenciatura analisada"].value_counts().to_string())
    grupos_novos = [c for c in novos["Curso/licenciatura analisada"].unique()
                    if c not in GRUPO]
    if grupos_novos:
        print(f"\n  ⚠️ Cursos SEM mapeamento (entrarão como grupo próprio): {grupos_novos}")

    # 2-6. limpeza + montagem
    uni = Unificador(con)
    next_id = int(con["id"].max()) + 1
    rows = []
    for i, (_, r) in enumerate(novos.iterrows()):
        cur = r["Curso/licenciatura analisada"]
        ban = uni.clean_banca(r["Membros da banca examinadora, se houver"])
        ori = uni.clean_orient(r["Orientador/a"])
        mems = [m for m in ban.split(" | ") if m and keyf(m) != keyf(ori)] if ban else []
        row = {"id": next_id + i, "grupo_tcc": GRUPO.get(cur, cur),
               "curso_fonte": str(cur).replace("LEDUCAR –", "LEDUCARR –"),
               "orientador": ori,
               "banca_examinadora": ban if ban else "Não informado",
               "banca_membro_1": mems[0] if len(mems) > 0 else "",
               "banca_membro_2": mems[1] if len(mems) > 1 else "",
               "banca_membro_3": mems[2] if len(mems) > 2 else "",
               "banca_membro_4": mems[3] if len(mems) > 3 else "",
               "em_ambos_forms": False, "fonte": Path(novo_path).stem, "conflitos": None}
        for fcol, ccol in FORM2COL.items():
            row[ccol] = r.get(fcol, "")
        row["ano_defesa"] = ano_plausivel(row.get("ano_defesa", ""))
        rows.append(row)
    add = pd.DataFrame(rows)[con.columns.tolist()]

    # 7. relatório de conferência
    print(f"\n== NOMES A CONFERIR (fuzzy no limiar {LIMIAR_REVISAO}-{LIMIAR_FUZZY}) ==")
    if uni.revisar:
        for nm, match, sc in sorted(set(uni.revisar)):
            print(f"  '{nm}'  ~  '{match}'  ({sc}%)  <- confira se é a mesma pessoa")
    else:
        print("  (nenhum)")
    resid = re.compile(r"\b(Prof|Dr|Presidente|Membro|Curso|Universidade|UFRR|"
                       r"Palavras|chave)\b|[ºª]", re.I)
    sus = [(r["id"], v) for _, r in add.iterrows()
           for v in [r["banca_membro_1"], r["banca_membro_2"], r["banca_membro_3"],
                     r["banca_membro_4"], r["orientador"]]
           if v and resid.search(str(v))]
    print(f"\n== RESÍDUOS SUSPEITOS (devem ser 0) ==")
    print("  " + ("\n  ".join(f"id {i}: {v}" for i, v in sus) if sus else "(nenhum)"))

    if not aplicar:
        print(f"\n[SIMULAÇÃO] Nada foi gravado. Rode com --aplicar para anexar os "
              f"{len(add)} novos ao consolidado.")
        return

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(CONSOLIDADO, BACKUPS / f"corpus_tccs_consolidado_pre_{ts}.csv")
    pd.concat([con, add], ignore_index=True).to_csv(CONSOLIDADO, index=False)
    print(f"\n✓ Anexados {len(add)} TCCs (ids {next_id}–{next_id+len(add)-1}). "
          f"Backup salvo em outputs/backups/.")
    print("Próximos passos: rode analise_corpus.py, re-cure os rótulos TOPICOS, "
          "rode analise_por_curso.py, valide e publique (ver PROTOCOLO_DADOS.md).")


if __name__ == "__main__":
    main()

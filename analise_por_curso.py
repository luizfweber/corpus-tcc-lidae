#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise temática POR CURSO, em camadas — LIDAE/UFRR
============================================================================
Por que por curso: o LDA global apenas redescobria a divisão entre cursos
(Tópico≈Música, Tópico≈Insikiran). Olhar DENTRO de cada curso revela sub-temas
reais — mas só onde há documentos suficientes (CLAUDE.md §1, §2, §4).

TRÊS CAMADAS, segundo o N de cada curso (atualizado p/ 211 TCCs, 2026-06-19):
  • LDA (N alto):        Insikiran (81), História (47) e Pedagogia (29).
                          K pequeno, escolhido por ESTABILIDADE (ARI entre seeds).
  • Descritivo (N médio): Música (21), Matemática (15). Sem LDA — termos mais
                          frequentes + listagem. Modelar tópicos aqui seria ruído.
  • Listagem (N ínfimo):  LEDUCARR (10), Letras (7). Nenhuma
                          modelagem — só identificação dos trabalhos.

Gera DOIS artefatos (mesma fonte de verdade):
  outputs/analise/analise_por_curso.md    (leitura humana)
  outputs/analise/analise_por_curso.json  (consumido pelo dashboard)
Rodar:  python3 analise_por_curso.py
"""
import csv, re, json, unicodedata, warnings, itertools
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import adjusted_rand_score

warnings.filterwarnings("ignore")

BASE = Path(__file__).parent
CSV  = BASE / "outputs" / "corpus_tccs_consolidado.csv"
OUT_MD   = BASE / "outputs" / "analise" / "analise_por_curso.md"
OUT_JSON = BASE / "outputs" / "analise" / "analise_por_curso.json"

LDA_CURSOS = {"Insikiran": (2, 4), "Pedagogia": (2, 3), "História": (2, 4)}
DESCRITIVO = ["Música", "Matemática", "Ciências Biológicas"]
LISTAGEM   = ["Letras", "LEDUCARR"]

SEEDS_EST = list(range(8))
MAX_ITER  = 40

# ── pré-processamento IDÊNTICO a analise_corpus.py ───────────────────────────
STOPWORDS = set("""
a ao às até com da das de dem do dos e em entre é isso isto
já lhe lhes me mais mas meu minha nem no nos não o os ou
pela pelo por que se seu sua te teu tua têm um uma uns umas
ao aos aqui bem como ela ele eles elas era esse esta este
fazer foram foi há isso isto ja lá lhe mais meu muito nos
nossa nossas nosso nossos pelo pelos pois sendo ser sido
também têm teu tua você vocês ainda assim como desta deste
desde desta deste desses dessas através entre foram foram
deve devem dever ainda assim além após antes durante
""".split())
TERMOS_GENERICOS = set("""
trabalho conclusão objetivo pesquisa análise universidade
estudo artigo relato texto abordagem tema área campo forma
base partir meio modo sobre para como este essa esse
curso alunos professores escola educação ensino aprendizagem
partir resultado sendo também ainda assim forma sendo
acadêmico monografia licenciatura graduação formação sendo
presente resultado sendo sendo sendo
""".split())
STOP_ALL = STOPWORDS | TERMOS_GENERICOS


def limpa(texto):
    t = (texto or "").lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z\s]", " ", t)
    return " ".join(w for w in t.split() if len(w) >= 4 and w not in STOP_ALL)


_NAO_KW = re.compile(r'^\s*n[ãa]o\s*(info|se aplica)', re.I)

def palavras_chave_limpas(val):
    """Separa as palavras-chave e remove o rótulo 'Palavras-chave:' embutido."""
    if not val or _NAO_KW.match(str(val).strip()):
        return ""
    s = re.sub(r'^\s*palavras?[\s-]*chave[\s]*[:\-–]?\s*', '', str(val).strip(),
               flags=re.I)
    if ";" in s:    partes = re.split(r"[;\n]", s)
    elif "\n" in s: partes = s.split("\n")
    elif "," in s:  partes = s.split(",")
    else:           partes = s.split(".")
    return " ; ".join(t for t in (p.strip().strip(".;,").strip() for p in partes) if t)


def texto_de(r):
    return limpa((r.get("titulo", "") or "") + " " +
                 (r.get("resumo", "") or "") + " " +
                 palavras_chave_limpas(r.get("palavras_chave", "")))


def titulo_limpo(r):
    t = re.sub(r"\s+", " ", (r.get("titulo", "") or "").strip())
    return "[link — sem título textual]" if t.startswith("http") else (t or "—")


def info_tcc(r):
    return {"id": r.get("id", "?"), "ano": r.get("ano_defesa", "?"),
            "titulo": titulo_limpo(r)}


# ── carregamento ─────────────────────────────────────────────────────────────
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
for r in rows:
    r["_texto"] = texto_de(r)

md = []


def out(s=""):
    print(s)
    md.append(s)


def top_termos(sub, n=15):
    """Termos por frequência DOCUMENTAL (em quantos TCCs cada termo aparece)."""
    df = Counter()
    for r in sub:
        for w in set(r["_texto"].split()):
            df[w] += 1
    return df.most_common(n)


# ── CAMADA LDA ───────────────────────────────────────────────────────────────
def camada_lda(curso, k_lo, k_hi):
    sub = [r for r in rows if r["grupo_tcc"] == curso]
    textos = [r["_texto"] for r in sub]
    vec = CountVectorizer(max_df=0.7, min_df=2, max_features=400)
    X = vec.fit_transform(textos)
    vocab = vec.get_feature_names_out()

    diag = {}
    for K in range(k_lo, k_hi + 1):
        labels, perps = {}, []
        for s in SEEDS_EST:
            m = LatentDirichletAllocation(n_components=K, random_state=s,
                                          max_iter=MAX_ITER, learning_method="batch")
            labels[s] = m.fit_transform(X).argmax(axis=1)
            perps.append(m.perplexity(X))
        aris = [adjusted_rand_score(labels[a], labels[b])
                for a, b in itertools.combinations(SEEDS_EST, 2)]
        diag[K] = float(np.mean(aris))
    K_best = max(diag, key=diag.get)
    ari = diag[K_best]

    lda = LatentDirichletAllocation(n_components=K_best, random_state=42,
                                    max_iter=MAX_ITER, learning_method="batch")
    dt = lda.fit_transform(X)
    dom = dt.argmax(axis=1)

    subtemas = []
    for t in range(K_best):
        termos = [vocab[i] for i in lda.components_[t].argsort()[-10:][::-1]]
        exemplos = [info_tcc(sub[i]) for i in np.argsort(dt[:, t])[::-1][:3]
                    if dom[i] == t]
        subtemas.append({"termos": termos, "n": int((dom == t).sum()),
                         "exemplos": exemplos})

    # markdown
    diag_txt = " · ".join(f"K{k}: ARI={v:.2f}" for k, v in diag.items())
    out(f"### {curso} — {len(sub)} TCCs · LDA intra-curso (K={K_best})")
    out(f"*Seleção de K por estabilidade entre 8 seeds — {diag_txt}. "
        f"Escolhido K={K_best} (ARI={ari:.2f}).*")
    if ari < 0.4:
        out(f"> ⚠️ Estabilidade baixa (ARI={ari:.2f}): sub-temas FRÁGEIS, "
            "indício a confirmar por leitura — não conclusão.")
    out("")
    for n, st_ in enumerate(subtemas, 1):
        out(f"**Sub-tema {n}** ({st_['n']} TCCs) — {', '.join(st_['termos'])}")
        for e in st_["exemplos"]:
            out(f"   - id {e['id']} ({e['ano']}): {e['titulo'][:90]}")
        out("")
    out("")

    return {"curso": curso, "n": len(sub), "camada": "lda",
            "top_termos": top_termos(sub), "tccs": [info_tcc(r) for r in sub],
            "lda": {"K": K_best, "ari": round(ari, 3), "diag": diag,
                    "subtemas": subtemas}}


# ── CAMADA DESCRITIVA ────────────────────────────────────────────────────────
def camada_descritiva(curso):
    sub = [r for r in rows if r["grupo_tcc"] == curso]
    top = top_termos(sub)
    out(f"### {curso} — {len(sub)} TCCs · descritivo (sem LDA)")
    out(f"*N insuficiente para modelagem de tópicos; reporta-se a frequência "
        f"documental dos termos e a lista de trabalhos.*\n")
    out(f"**Termos mais recorrentes (nº de TCCs):** "
        f"{', '.join(f'{w} ({n})' for w, n in top)}\n")
    out("**Trabalhos:**")
    for r in sorted(sub, key=lambda r: str(r.get("ano_defesa", ""))):
        out(f"   - id {r.get('id','?')} ({r.get('ano_defesa','?')}): "
            f"{titulo_limpo(r)[:90]}")
    out("")
    return {"curso": curso, "n": len(sub), "camada": "descritivo",
            "top_termos": top, "tccs": [info_tcc(r) for r in sub], "lda": None}


# ── CAMADA LISTAGEM ──────────────────────────────────────────────────────────
def camada_listagem(curso):
    sub = [r for r in rows if r["grupo_tcc"] == curso]
    out(f"### {curso} — {len(sub)} TCCs · listagem (sem análise)")
    out(f"*N ínfimo ({len(sub)}): qualquer modelagem seria artefato "
        f"(CLAUDE.md §1). Apenas identificação.*\n")
    for r in sorted(sub, key=lambda r: str(r.get("ano_defesa", ""))):
        out(f"   - id {r.get('id','?')} ({r.get('ano_defesa','?')}): "
            f"{titulo_limpo(r)[:110]}")
    out("")
    return {"curso": curso, "n": len(sub), "camada": "listagem",
            "top_termos": [], "tccs": [info_tcc(r) for r in sub], "lda": None}


# ── execução ─────────────────────────────────────────────────────────────────
out("# Análise temática por curso, em camadas — LIDAE/UFRR\n")
out(f"Corpus: {len(rows)} TCCs. Tratamento conforme o N de cada curso "
    "(LDA · descritivo · listagem). Exploratório, não censitário.\n")

registros = []

out("\n## 🟢 Camada LDA (N suficiente para sub-temas)\n")
for curso, (lo, hi) in LDA_CURSOS.items():
    registros.append(camada_lda(curso, lo, hi))

out("\n## 🟠 Camada descritiva (N médio — termos + leitura)\n")
for curso in DESCRITIVO:
    registros.append(camada_descritiva(curso))

out("\n## 🔴 Camada listagem (N ínfimo — sem modelagem)\n")
for curso in LISTAGEM:
    registros.append(camada_listagem(curso))

OUT_MD.write_text("\n".join(md), encoding="utf-8")
OUT_JSON.write_text(json.dumps(
    {"gerado_em": date.today().isoformat(), "n_total": len(rows),
     "cursos": registros}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ Relatório salvo em: {OUT_MD}")
print(f"✓ JSON salvo em:      {OUT_JSON}")

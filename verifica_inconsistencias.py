#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de inconsistências para revisão MANUAL — LIDAE/UFRR
============================================================================
Varre o corpus e SINALIZA registros com dados suspeitos nos campos título,
resumo, autor, palavras-chave, tipo de TCC e ano. NÃO corrige nada — apenas
gera uma planilha editável para verificação humana (CLAUDE.md §2, §3:
nunca imputar, nunca "corrigir" em silêncio).

Saídas:
  VERIFICACAO_DADOS.xlsx   (editável — aba 'verificar' + aba 'resumo_problemas')
  VERIFICACAO_DADOS.csv    (mesma tabela, formato simples)
Rodar:  python3 verifica_inconsistencias.py
"""
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
FONTE = BASE / "outputs" / "corpus_tccs_consolidado.csv"
OUT_XLSX = BASE / "VERIFICACAO_DADOS.xlsx"
OUT_CSV  = BASE / "VERIFICACAO_DADOS.csv"

df = pd.read_csv(FONTE, dtype=str).fillna("")


def v(row, campo):
    return str(row.get(campo, "")).strip()


def norm_resumo(s):
    return re.sub(r"\s+", " ", s.lower().strip())[:120]


# duplicatas de resumo (mesmo texto em ids diferentes)
mapa_resumo = defaultdict(list)
for _, r in df.iterrows():
    res = v(r, "resumo")
    if len(res) >= 40:
        mapa_resumo[norm_resumo(res)].append(str(r.get("id", "?")))
dup_resumo = {k: ids for k, ids in mapa_resumo.items() if len(ids) > 1}


def problemas_da_linha(r):
    p = []
    idr = str(r.get("id", "?"))
    titulo = v(r, "titulo")
    resumo = v(r, "resumo")
    autor  = v(r, "autor")
    pchave = v(r, "palavras_chave")
    tipo   = v(r, "tipo_tcc")
    ano    = v(r, "ano_defesa")

    # ── título
    if not titulo:
        p.append("título vazio")
    elif titulo.lower().startswith("http"):
        p.append("título é um link (URL)")
    elif len(titulo) < 15:
        p.append("título muito curto")

    # ── resumo
    if not resumo:
        p.append("resumo vazio")
    else:
        if resumo.lower().startswith("http"):
            p.append("resumo é um link (URL)")
        elif len(resumo) < 60:
            p.append("resumo muito curto (possível placeholder)")
        if re.match(r"^\s*resumo\b", resumo, flags=re.I):
            p.append("resumo começa com 'Resumo' (limpeza pendente)")
        if re.search(r"palavras[-\s]?chave", resumo, flags=re.I):
            p.append("resumo contém 'palavras-chave' (limpeza pendente)")
        chave = norm_resumo(resumo)
        if chave in dup_resumo:
            outros = [i for i in dup_resumo[chave] if i != idr]
            if outros:
                p.append(f"resumo idêntico ao(s) id(s): {', '.join(outros)}")

    # ── autor
    if not autor:
        p.append("autor vazio")
    elif len(autor) < 5:
        p.append("autor muito curto")
    elif any(c.isdigit() for c in autor):
        p.append("autor contém números")
    elif "http" in autor.lower():
        p.append("autor contém URL")

    # ── palavras-chave
    if not pchave:
        p.append("palavras-chave vazias")
    else:
        if re.match(r"^\s*palavras[-\s]?chave", pchave, flags=re.I):
            p.append("palavras-chave com rótulo redundante")
        if len(pchave) > 200:
            p.append("palavras-chave muito longas (pode conter resumo)")
        if "http" in pchave.lower():
            p.append("palavras-chave contêm URL")

    # ── tipo de TCC
    if tipo.lower() in ("", "nan", "não informado", "nao informado", "não se aplica"):
        p.append("tipo de TCC ausente/indefinido")

    # ── ano de defesa
    if ano.lower() in ("", "0000", "não informado", "nao informado", "não se aplica"):
        p.append("ano de defesa ausente/inválido")
    elif not re.fullmatch(r"(19|20)\d{2}", ano):
        p.append(f"ano de defesa fora do padrão ('{ano}')")

    return p


# problemas de CONTEÚDO (os "dados estranhos") vs lacunas conhecidas (tipo/ano)
def prioridade(probs):
    conteudo = [x for x in probs
                if not x.startswith("tipo de TCC")
                and not x.startswith("ano de defesa")]
    return "ALTA" if conteudo else "baixa"


# monta tabela de flagrados
registros = []
for _, r in df.iterrows():
    probs = problemas_da_linha(r)
    if probs:
        registros.append({
            "id": r.get("id", "?"),
            "PRIORIDADE": prioridade(probs),
            "grupo_tcc": v(r, "grupo_tcc"),
            "curso_fonte": v(r, "curso_fonte"),
            "PROBLEMAS_DETECTADOS": " | ".join(probs),
            "n_problemas": len(probs),
            "titulo": v(r, "titulo"),
            "autor": v(r, "autor"),
            "ano_defesa": v(r, "ano_defesa"),
            "tipo_tcc": v(r, "tipo_tcc"),
            "palavras_chave": v(r, "palavras_chave"),
            "resumo": v(r, "resumo"),
            "CORRECAO_SUGERIDA": "",   # preencher manualmente
            "VERIFICADO_OK": "",       # marcar 'x' quando conferido
        })

ordem_pri = {"ALTA": 0, "baixa": 1}
flag = pd.DataFrame(registros)
flag["_o"] = flag["PRIORIDADE"].map(ordem_pri)
flag = (flag.sort_values(["_o", "n_problemas", "id"],
                         ascending=[True, False, True])
            .drop(columns="_o"))

alta  = flag[flag["PRIORIDADE"] == "ALTA"]
baixa = flag[flag["PRIORIDADE"] == "baixa"]

# contagem por tipo de problema
cont = Counter()
for reg in registros:
    for prob in reg["PROBLEMAS_DETECTADOS"].split(" | "):
        cont[re.sub(r"\s*\(.*?\)|:.*$", "", prob).strip()] += 1
resumo_tab = pd.DataFrame(sorted(cont.items(), key=lambda x: -x[1]),
                          columns=["tipo_de_problema", "ocorrencias"])


def formata(ws):
    from openpyxl.styles import Alignment
    larg = {"A": 6, "B": 10, "C": 14, "D": 30, "E": 44, "F": 5, "G": 50,
            "H": 22, "I": 12, "J": 18, "K": 40, "L": 60, "M": 30, "N": 13}
    for col, w in larg.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")


# grava: aba 'campos_estranhos' (prioridade) + 'tipo_e_ano' + resumo
with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xl:
    alta.to_excel(xl, sheet_name="campos_estranhos", index=False)
    baixa.to_excel(xl, sheet_name="tipo_e_ano", index=False)
    resumo_tab.to_excel(xl, sheet_name="resumo_problemas", index=False)
    formata(xl.sheets["campos_estranhos"])
    formata(xl.sheets["tipo_e_ano"])

flag.to_csv(OUT_CSV, index=False, encoding="utf-8")

# relatório no console
print(f"Corpus: {len(df)} TCCs · flagrados: {len(flag)} "
      f"(🔴 {len(alta)} com campo estranho · {len(baixa)} só tipo/ano)\n")
print("Problemas por tipo:")
for t, n in resumo_tab.itertuples(index=False):
    print(f"  {n:>3}  {t}")

print("\n🔴 PRIORIDADE ALTA — campos com dado estranho:")
for _, r in alta.iterrows():
    print(f"  id {r['id']:>3} ({r['grupo_tcc']}): {r['PROBLEMAS_DETECTADOS']}")

print(f"\n✓ Planilha editável: {OUT_XLSX.name}  (abas: campos_estranhos · "
      f"tipo_e_ano · resumo_problemas)")
print(f"✓ CSV:               {OUT_CSV.name}")

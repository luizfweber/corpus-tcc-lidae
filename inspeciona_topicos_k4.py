#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspeção qualitativa dos tópicos LDA com K=4 — LIDAE/UFRR
============================================================================
Objetivo: dar BASE DE LEITURA para rotular os tópicos (CLAUDE.md §4 — o rótulo
sai da leitura dos documentos, não só dos top-termos). Não altera modelo/dados.

Para cada tópico (K=4, seed 42, igual ao pipeline) imprime:
  • os 12 termos mais prováveis;
  • os 5 TCCs mais representativos (maior probabilidade do tópico): id, grupo,
    ano, título e trecho do resumo;
  • a distribuição tópico × grupo de curso.

Salva também outputs/analise/topicos_K4_para_revisao.md para registro.
Rodar:  python3 inspeciona_topicos_k4.py
"""
import csv, re, unicodedata, warnings
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

warnings.filterwarnings("ignore")

K        = 4
SEED     = 42
MAX_ITER = 30
N_TERMOS = 12
N_DOCS   = 5

BASE = Path(__file__).parent
CSV  = BASE / "outputs" / "corpus_tccs_consolidado.csv"
OUT  = BASE / "outputs" / "analise" / "topicos_K4_para_revisao.md"

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


# ── carregamento e ajuste ────────────────────────────────────────────────────
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
textos = [
    limpa((r.get("titulo", "") or "") + " " +
          (r.get("resumo", "") or "") + " " +
          (r.get("palavras_chave", "") or ""))
    for r in rows
]
vec = CountVectorizer(max_df=0.6, min_df=2, max_features=800)
X = vec.fit_transform(textos)
vocab = vec.get_feature_names_out()

lda = LatentDirichletAllocation(n_components=K, random_state=SEED,
                                max_iter=MAX_ITER, learning_method="batch")
doc_topic = lda.fit_transform(X)
dom = doc_topic.argmax(axis=1)

linhas = []  # acumula markdown


def out(s=""):
    print(s)
    linhas.append(s)


out(f"# Tópicos LDA (K={K}, seed {SEED}) — base para revisão de rótulos\n")
out(f"Corpus: {len(rows)} TCCs · vocabulário: {len(vocab)} termos\n")
out("> Os rótulos devem sair da LEITURA dos documentos abaixo, não só dos "
    "top-termos (CLAUDE.md §4). Tópico = indício, não categoria fechada.\n")

for t in range(K):
    termos = [vocab[i] for i in lda.components_[t].argsort()[-N_TERMOS:][::-1]]
    n_dom = int((dom == t).sum())
    out("\n" + "═" * 74)
    out(f"## TÓPICO {t}  ·  {n_dom} TCCs dominantes")
    out("═" * 74)
    out(f"**Top-{N_TERMOS} termos:** {', '.join(termos)}\n")

    # distribuição por grupo entre os dominantes
    grupos = Counter(rows[i].get("grupo_tcc", "?") for i in range(len(rows))
                     if dom[i] == t)
    dist = " · ".join(f"{g}: {n}" for g, n in grupos.most_common())
    out(f"**Grupos:** {dist}\n")

    # 5 documentos mais representativos
    idx_ord = np.argsort(doc_topic[:, t])[::-1][:N_DOCS]
    out(f"**{N_DOCS} TCCs mais representativos (maior probabilidade):**\n")
    for rank, i in enumerate(idx_ord, 1):
        r = rows[i]
        prob = doc_topic[i, t]
        titulo = (r.get("titulo", "") or "").strip()
        resumo = re.sub(r"\s+", " ", (r.get("resumo", "") or "").strip())
        snippet = (resumo[:240] + "…") if len(resumo) > 240 else (resumo or "—")
        out(f"{rank}. **id {r.get('id','?')}** · {r.get('grupo_tcc','?')} · "
            f"{r.get('ano_defesa','?')} · p={prob:.2f}")
        out(f"   *{titulo}*")
        out(f"   {snippet}\n")

OUT.write_text("\n".join(linhas), encoding="utf-8")
print(f"\n✓ Registro salvo em: {OUT}")

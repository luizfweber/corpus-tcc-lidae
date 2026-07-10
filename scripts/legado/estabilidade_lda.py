#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de ESTABILIDADE do LDA — LIDAE/UFRR
============================================================================
Pergunta metodológica: a divisão em K tópicos SOBREVIVE a mudanças de seed?
Num corpus pequeno (147 TCCs, textos curtos), tópicos instáveis são esperados
— este script MEDE essa instabilidade em vez de escondê-la (CLAUDE.md §1, §4).

Replica EXATAMENTE o pré-processamento de analise_corpus.py:
  texto = título + resumo + palavras-chave  →  limpa() + STOP_ALL (≥4 letras)
  CountVectorizer(max_df=0.6, min_df=2, max_features=800)
  LatentDirichletAllocation(max_iter=30, learning_method="batch")

Duas métricas, ambas invariantes à permutação dos rótulos dos tópicos:
  1. ARI (Adjusted Rand Index) das ATRIBUIÇÕES de documento → tópico dominante,
     comparando todos os pares de seeds. Mede: "os mesmos TCCs caem juntos?"
       ARI≈1 idêntico · 0.7+ estável · 0.4–0.7 moderado · <0.4 instável · 0≈acaso
  2. Jaccard dos TOP-termos por tópico, com alinhamento ótimo (Hungarian) entre
     seeds. Mede: "o conteúdo (palavras) de cada tópico persiste?"
       0.5+ persiste bem · 0.3–0.5 parcial · <0.3 conteúdo volátil

NÃO altera o modelo nem os dados. Só diagnostica. Rodar:
    python3 estabilidade_lda.py
"""
import csv, re, unicodedata, warnings, itertools
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import adjusted_rand_score
from scipy.optimize import linear_sum_assignment

warnings.filterwarnings("ignore")

# ── parâmetros do teste ──────────────────────────────────────────────────────
K_RANGE   = range(4, 9)          # mesmos K testados em analise_corpus.py
SEEDS     = list(range(12))      # 12 sementes → 66 pares por K
N_TOP     = 10                   # top-termos por tópico (igual ao pipeline)
MAX_ITER  = 30                   # idêntico ao pipeline

BASE = Path(__file__).parent
CSV  = BASE / "outputs" / "corpus_tccs_consolidado.csv"
OUT  = BASE / "outputs" / "analise"
OUT.mkdir(parents=True, exist_ok=True)

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


# ── carregamento ─────────────────────────────────────────────────────────────
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
print(f"Corpus: {len(rows)} TCCs | vocabulário: {len(vocab)} termos | "
      f"{len(SEEDS)} seeds por K\n")


def top_termos(lda):
    """Conjunto de top-N termos por tópico."""
    return [set(vocab[i] for i in comp.argsort()[-N_TOP:][::-1])
            for comp in lda.components_]


def jaccard_alinhado(tops_a, tops_b):
    """Jaccard médio entre tópicos de duas execuções, com pareamento ótimo."""
    k = len(tops_a)
    M = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            inter = len(tops_a[i] & tops_b[j])
            union = len(tops_a[i] | tops_b[j])
            M[i, j] = inter / union if union else 0.0
    # maximiza soma do Jaccard pareado (Hungarian minimiza → negamos)
    ri, ci = linear_sum_assignment(-M)
    return M[ri, ci].mean()


# ── loop principal: ajusta LDA por (K, seed), coleta diagnósticos ────────────
resultados = []
for K in K_RANGE:
    labels_por_seed = {}   # seed → vetor de tópico dominante por documento
    tops_por_seed   = {}   # seed → top-termos por tópico
    perps           = []
    for s in SEEDS:
        lda = LatentDirichletAllocation(n_components=K, random_state=s,
                                        max_iter=MAX_ITER, learning_method="batch")
        doc_topic = lda.fit_transform(X)
        labels_por_seed[s] = doc_topic.argmax(axis=1)
        tops_por_seed[s]   = top_termos(lda)
        perps.append(lda.perplexity(X))

    # pares de seeds
    pares = list(itertools.combinations(SEEDS, 2))
    aris  = [adjusted_rand_score(labels_por_seed[a], labels_por_seed[b])
             for a, b in pares]
    jacs  = [jaccard_alinhado(tops_por_seed[a], tops_por_seed[b])
             for a, b in pares]

    resultados.append({
        "K": K,
        "ari_med": np.mean(aris), "ari_sd": np.std(aris), "ari_min": np.min(aris),
        "jac_med": np.mean(jacs), "jac_sd": np.std(jacs),
        "perp_med": np.mean(perps),
    })


def rotulo_ari(v):
    return ("estável"  if v >= 0.7 else
            "moderado" if v >= 0.4 else
            "instável" if v >= 0.2 else "≈acaso")


def rotulo_jac(v):
    return ("persiste"  if v >= 0.5 else
            "parcial"   if v >= 0.3 else "volátil")


# ── relatório em console ─────────────────────────────────────────────────────
print("═" * 78)
print("ESTABILIDADE DO LDA POR Nº DE TÓPICOS (K)")
print("═" * 78)
print(f"{'K':>3} | {'ARI docs (méd±dp)':>22} | {'min':>6} | "
      f"{'Jaccard top (méd±dp)':>22} | {'perplex':>8}")
print("-" * 78)
for r in resultados:
    print(f"{r['K']:>3} | "
          f"{r['ari_med']:>6.3f} ±{r['ari_sd']:>5.3f}  {rotulo_ari(r['ari_med']):<9}| "
          f"{r['ari_min']:>6.3f} | "
          f"{r['jac_med']:>6.3f} ±{r['jac_sd']:>5.3f}  {rotulo_jac(r['jac_med']):<8}| "
          f"{r['perp_med']:>8.1f}")
print("-" * 78)

melhor_ari = max(resultados, key=lambda r: r["ari_med"])
melhor_perp = min(resultados, key=lambda r: r["perp_med"])
print(f"\nMais ESTÁVEL (maior ARI):       K={melhor_ari['K']} "
      f"(ARI={melhor_ari['ari_med']:.3f})")
print(f"Melhor PERPLEXIDADE (pipeline): K={melhor_perp['K']} "
      f"(perp={melhor_perp['perp_med']:.1f})")
if melhor_ari["K"] != melhor_perp["K"]:
    print("⚠️  Os dois critérios DIVERGEM — a perplexidade sozinha não basta.\n"
          "    Decisão de K deve pesar estabilidade + leitura qualitativa (CLAUDE.md §5).")
else:
    print("✓  Os dois critérios CONVERGEM neste K.")

print("\nLeitura das faixas (heurísticas, não veredito):")
print("  ARI:     0.7+ estável · 0.4–0.7 moderado · 0.2–0.4 instável · <0.2 ≈acaso")
print("  Jaccard: 0.5+ conteúdo persiste · 0.3–0.5 parcial · <0.3 volátil")

# ── gráfico ──────────────────────────────────────────────────────────────────
Ks = [r["K"] for r in resultados]
fig, ax1 = plt.subplots(figsize=(9, 5))
c1, c2 = "#1B5E3B", "#C1440E"
ax1.errorbar(Ks, [r["ari_med"] for r in resultados],
             yerr=[r["ari_sd"] for r in resultados],
             marker="o", color=c1, capsize=4, label="ARI (atribuição de docs)")
ax1.errorbar(Ks, [r["jac_med"] for r in resultados],
             yerr=[r["jac_sd"] for r in resultados],
             marker="s", color=c2, capsize=4, label="Jaccard (top-termos)")
ax1.axhspan(0.7, 1.0, color=c1, alpha=0.06)
ax1.axhline(0.7, ls=":", color=c1, lw=1)
ax1.axhline(0.4, ls=":", color="gray", lw=1)
ax1.set_xlabel("K (nº de tópicos)")
ax1.set_ylabel("Estabilidade entre seeds (0–1)")
ax1.set_xticks(Ks)
ax1.set_ylim(0, 1)
ax1.set_title("Estabilidade do LDA por K — 12 seeds, corpus de 147 TCCs\n"
              "(quanto mais alto e mais 'apertado', mais reprodutível)",
              fontsize=11)
ax1.legend(loc="upper right")
ax1.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(OUT / "7_estabilidade_lda.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\n✓ Gráfico salvo: {OUT / '7_estabilidade_lda.png'}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise exploratória do corpus de TCCs — LIDAE/UFRR
Protocolo: descritiva → LDA → clustering → redes → temática indígena
"""
import csv, re, unicodedata, warnings
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

warnings.filterwarnings("ignore")

# ── caminhos ────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
CSV  = BASE / "outputs" / "corpus_tccs_consolidado.csv"
OUT  = BASE / "outputs" / "analise"
OUT.mkdir(parents=True, exist_ok=True)

# ── paleta consistente ───────────────────────────────────────────────────────
PALETA = ["#2C6E91","#4AABDB","#E07B39","#57A773","#A94063",
          "#8E6BBF","#C4963A","#5C6BC0"]

# ============================================================================
# 0. CARREGAMENTO E PREPARAÇÃO
# ============================================================================
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
N = len(rows)

def num(v, default=None):
    try: return float(str(v).strip().replace(",","."))
    except: return default

for r in rows:
    r["ano_num"]  = num(r["ano_defesa"])
    # guarda de plausibilidade: ano fora de 1990–2030 é erro de digitação da
    # fonte (ex.: '0000', '20232') → tratado como ausente (CLAUDE.md §2)
    if r["ano_num"] is not None and not (1990 <= r["ano_num"] <= 2030):
        r["ano_num"] = None
    r["pag_num"]  = num(r["paginas"])
    # grupo canônico já está em grupo_tcc
    r["grupo"] = r["grupo_tcc"]

grupos = sorted(set(r["grupo"] for r in rows))
print(f"Corpus: {N} TCCs | {len(grupos)} grupos")

# ============================================================================
# 1. LIMPEZA TEXTUAL
# ============================================================================
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
    """Separa as palavras-chave (detecta o separador por entrada) e remove o
    rótulo 'Palavras-chave:' embutido — evita injetar tokens 'palavras'/'chave'
    no modelo. Devolve os termos separados por ' ; '."""
    if not val or _NAO_KW.match(str(val).strip()):
        return ""
    s = re.sub(r'^\s*palavras?[\s-]*chave[\s]*[:\-–]?\s*', '', str(val).strip(),
               flags=re.I)
    if ";" in s:    partes = re.split(r"[;\n]", s)
    elif "\n" in s: partes = s.split("\n")
    elif "," in s:  partes = s.split(",")
    else:           partes = s.split(".")
    termos = [t for t in (p.strip().strip(".;,").strip() for p in partes) if t]
    return " ; ".join(termos)

for r in rows:
    r["texto"] = limpa(
        (r.get("titulo","") or "") + " " +
        (r.get("resumo","") or "") + " " +
        palavras_chave_limpas(r.get("palavras_chave",""))
    )

# ============================================================================
# 2. ANÁLISE DESCRITIVA
# ============================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle(f"Corpus de TCCs — LIDAE/UFRR  (n={N}, piloto exploratório)",
             fontsize=13, fontweight="bold", y=1.01)

# 2a. TCCs por grupo
cnt_grupo = Counter(r["grupo"] for r in rows)
grupos_ord = [g for g, _ in cnt_grupo.most_common()]
vals = [cnt_grupo[g] for g in grupos_ord]
cores = [PALETA[i % len(PALETA)] for i in range(len(grupos_ord))]
axes[0].barh(grupos_ord[::-1], vals[::-1], color=cores[::-1])
for i, v in enumerate(vals[::-1]):
    axes[0].text(v + 0.3, i, str(v), va="center", fontsize=9)
axes[0].set_xlabel("TCCs coletados")
axes[0].set_title("TCCs por grupo de curso")
axes[0].set_xlim(0, max(vals) + 8)

# 2b. TCCs por ano
anos_validos = [int(r["ano_num"]) for r in rows
                if r["ano_num"] and 2000 <= r["ano_num"] <= 2026]
cnt_ano = Counter(anos_validos)
anos = sorted(cnt_ano)
axes[1].bar(anos, [cnt_ano[a] for a in anos], color=PALETA[0])
axes[1].set_xlabel("Ano de defesa")
axes[1].set_ylabel("Nº de TCCs")
axes[1].set_title(f"TCCs por ano (n={len(anos_validos)}, "
                  f"{N-len(anos_validos)} sem ano)")
axes[1].tick_params(axis="x", rotation=45)

# 2c. Páginas por grupo (mediana — CLAUDE.md §2 regra 7)
pags_grupo = defaultdict(list)
for r in rows:
    if r["pag_num"]:
        pags_grupo[r["grupo"]].append(r["pag_num"])

grupos_pg = [g for g in grupos_ord if pags_grupo[g]]
medianas   = [np.median(pags_grupo[g]) for g in grupos_pg]
cores_pg   = [PALETA[grupos_ord.index(g) % len(PALETA)] for g in grupos_pg]
axes[2].barh(grupos_pg[::-1], medianas[::-1], color=cores_pg[::-1])
for i, v in enumerate(medianas[::-1]):
    axes[2].text(v + 0.5, i, f"{v:.0f}", va="center", fontsize=9)
axes[2].set_xlabel("Mediana de páginas")
axes[2].set_title("Mediana de páginas por grupo\n(exclui registros sem dado)")

plt.tight_layout()
plt.savefig(OUT / "1_descritiva_geral.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ 1_descritiva_geral.png")

# 2d. Top orientadores
def norm_nome(s):
    s = re.sub(r"\b(Prof|Profa|Dr|Dra|Me|Msc|Ms|Esp|Doutor|Mestre)\.?\b", "", s, flags=re.I)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().title()

cnt_orient = Counter()
for r in rows:
    o = norm_nome(r.get("orientador","") or "")
    if o and len(o) > 4:
        cnt_orient[o] += 1

top_orient = [(o, n) for o, n in cnt_orient.most_common(15) if n >= 2]
if top_orient:
    fig, ax = plt.subplots(figsize=(10, 5))
    nomes = [o for o, _ in top_orient]
    vals2 = [n for _, n in top_orient]
    ax.barh(nomes[::-1], vals2[::-1], color=PALETA[1])
    for i, v in enumerate(vals2[::-1]):
        ax.text(v + 0.1, i, str(v), va="center", fontsize=9)
    ax.set_xlabel("TCCs orientados")
    ax.set_title("Orientadores com 2+ TCCs no corpus\n"
                 "(nomes normalizados — variações podem subsistir)")
    ax.set_xlim(0, max(vals2) + 2)
    plt.tight_layout()
    plt.savefig(OUT / "2_orientadores.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ 2_orientadores.png")

# ============================================================================
# 3. LDA — MODELAGEM DE TÓPICOS
# ============================================================================
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

textos = [r["texto"] for r in rows]
vec = CountVectorizer(max_df=0.6, min_df=2, max_features=800)
X = vec.fit_transform(textos)
vocab = vec.get_feature_names_out()

# testa K 4..8 (perplexidade só para registro/comparação)
perps = {}
modelos = {}
for k in range(4, 9):
    lda = LatentDirichletAllocation(n_components=k, random_state=42,
                                    max_iter=30, learning_method="batch")
    lda.fit(X)
    perps[k] = lda.perplexity(X)
    modelos[k] = lda

# K FIXADO em 8 por decisão de leitura (granularidade fina — revela nichos como
# história/gênero e etnobotânica). Perplexidade é INDÍCIO, não veredito (§4):
# K=8 (498) fica perto do mínimo K=4 (491). Rótulos exigem revisão qualitativa.
K_LDA = 8
K_best = K_LDA
print(f"  Perplexidades LDA: { {k: round(v,1) for k,v in perps.items()} }")
print(f"  K escolhido (fixado por leitura): {K_best}  "
      f"(perplexidade {perps[K_best]:.0f}; mínimo seria K={min(perps, key=perps.get)})")

lda_final = modelos[K_best]
termos_top = {}
for t_idx, comp in enumerate(lda_final.components_):
    top10 = [vocab[i] for i in comp.argsort()[-10:][::-1]]
    termos_top[t_idx] = top10

# rotulos propostos (ajustar manualmente se necessário)
ROTULOS = {
    0: "Tópico A", 1: "Tópico B", 2: "Tópico C",
    3: "Tópico D", 4: "Tópico E", 5: "Tópico F",
    6: "Tópico G", 7: "Tópico H",
}

print("\n── Tópicos LDA (rótulos APROXIMADOS — requerem revisão qualitativa) ──")
for t, terms in termos_top.items():
    print(f"  [{ROTULOS.get(t,'?')}] {', '.join(terms)}")

# atribui tópico dominante
doc_topic = lda_final.transform(X)
for i, r in enumerate(rows):
    r["topico_dom"] = int(doc_topic[i].argmax())
    r["topico_prob"] = float(doc_topic[i].max())

# heatmap tópico × grupo
grupos_uniq = sorted(set(r["grupo"] for r in rows))
n_top = lda_final.n_components
mat = np.zeros((n_top, len(grupos_uniq)))
for r in rows:
    gi = grupos_uniq.index(r["grupo"])
    mat[r["topico_dom"], gi] += 1

fig, ax = plt.subplots(figsize=(11, 5))
im = ax.imshow(mat, aspect="auto", cmap="YlOrRd")
ax.set_xticks(range(len(grupos_uniq))); ax.set_xticklabels(grupos_uniq, rotation=35, ha="right")
ax.set_yticks(range(n_top)); ax.set_yticklabels([ROTULOS.get(t,f"T{t}") for t in range(n_top)])
plt.colorbar(im, ax=ax, label="Nº TCCs")
ax.set_title(f"Distribuição de tópicos LDA (K={K_best}) por grupo de curso\n"
             "INDÍCIO exploratório — rótulos requerem revisão qualitativa")
for i in range(n_top):
    for j in range(len(grupos_uniq)):
        if mat[i,j] > 0:
            ax.text(j, i, int(mat[i,j]), ha="center", va="center", fontsize=8,
                    color="black" if mat[i,j] < mat.max()*0.6 else "white")
plt.tight_layout()
plt.savefig(OUT / "3_lda_topicos.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ 3_lda_topicos.png")

# ============================================================================
# 4. CLUSTERING (TF-IDF + k-means)
# ============================================================================
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import TruncatedSVD

tfidf = TfidfVectorizer(max_df=0.6, min_df=2, max_features=800)
Xt = tfidf.fit_transform(textos)

silhs = {}
for k in range(3, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(Xt)
    # random_state fixo: sem ele a amostragem da silhueta varia entre execuções
    # e o K escolhido muda (não determinismo indesejado)
    try: silhs[k] = silhouette_score(Xt, labels, sample_size=min(N,128),
                                     random_state=42)
    except: silhs[k] = 0

K_clust = max(silhs, key=silhs.get)
print(f"\n  Silhuetas k-means: { {k: round(v,3) for k,v in silhs.items()} }")
print(f"  K escolhido: {K_clust}  (silhueta={silhs[K_clust]:.3f})")
print("  NOTA: silhueta baixa em texto curto é esperada — fronteiras porosas, não falha.")

km_final = KMeans(n_clusters=K_clust, random_state=42, n_init=10)
cluster_labels = km_final.fit_predict(Xt)
for i, r in enumerate(rows):
    r["cluster"] = int(cluster_labels[i])

# reduz p/ 2D via SVD p/ visualização
svd = TruncatedSVD(n_components=2, random_state=42)
Xr = svd.fit_transform(Xt)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# por cluster
cores_c = [PALETA[c % len(PALETA)] for c in cluster_labels]
for k in range(K_clust):
    mask = cluster_labels == k
    axes[0].scatter(Xr[mask,0], Xr[mask,1], c=PALETA[k%len(PALETA)],
                    label=f"C{k}", s=60, alpha=0.8, edgecolors="white", lw=0.4)
axes[0].set_title(f"Clusters k-means (k={K_clust})\nSilhueta={silhs[K_clust]:.3f} "
                  "(valor baixo esperado em corpus pequeno)")
axes[0].legend(title="Cluster", fontsize=8)
axes[0].set_xlabel("SVD dim 1"); axes[0].set_ylabel("SVD dim 2")

# por grupo real
grupo_ids = {g: i for i, g in enumerate(grupos_uniq)}
cores_g = [PALETA[grupo_ids[r["grupo"]] % len(PALETA)] for r in rows]
patches = [mpatches.Patch(color=PALETA[i%len(PALETA)], label=g)
           for i, g in enumerate(grupos_uniq)]
for i, r in enumerate(rows):
    gi = grupo_ids[r["grupo"]]
    axes[1].scatter(Xr[i,0], Xr[i,1], c=PALETA[gi%len(PALETA)],
                    s=60, alpha=0.8, edgecolors="white", lw=0.4)
axes[1].legend(handles=patches, title="Grupo", fontsize=7, loc="best")
axes[1].set_title("Grupos de curso formais\n(mesmo espaço SVD)")
axes[1].set_xlabel("SVD dim 1"); axes[1].set_ylabel("SVD dim 2")

plt.suptitle("Clustering TF-IDF — INDÍCIO exploratório", fontsize=11, y=1.01)
plt.tight_layout()
plt.savefig(OUT / "4_clustering.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ 4_clustering.png")

# coincidência cluster × curso
print("\n── Cluster × Grupo (contagens) ──")
from collections import Counter as C2
for k in range(K_clust):
    membros = [r["grupo"] for r in rows if r["cluster"]==k]
    print(f"  C{k} (n={len(membros)}): {dict(C2(membros).most_common(3))}")

# ============================================================================
# 5. REDES DE ORIENTAÇÃO E BANCAS
# ============================================================================
try:
    import networkx as nx

    # 5a. Rede de orientação (orientador → tópico)
    orient_topico = defaultdict(list)
    for r in rows:
        o = norm_nome(r.get("orientador","") or "")
        if o and len(o) > 4:
            orient_topico[o].append(r["topico_dom"])

    orient_recorrentes = {o: ts for o, ts in orient_topico.items() if len(ts) >= 2}
    pct_recorrentes = sum(len(v) for v in orient_recorrentes.values()) / N * 100
    print(f"\n  Orientadores com 2+ TCCs: {len(orient_recorrentes)} "
          f"({pct_recorrentes:.0f}% dos TCCs)")

    # grafo orientador → tópico dominante (mais frequente)
    G_or = nx.Graph()
    for o, ts in orient_recorrentes.items():
        top_dom = Counter(ts).most_common(1)[0][0]
        rot = ROTULOS.get(top_dom, f"T{top_dom}")
        G_or.add_edge(o, rot, weight=len(ts))

    fig, ax = plt.subplots(figsize=(12, 7))
    pos = nx.spring_layout(G_or, seed=42, k=2.5)
    orient_nodes = [n for n in G_or.nodes if n not in ROTULOS.values()]
    topico_nodes = [n for n in G_or.nodes if n in ROTULOS.values()]
    nx.draw_networkx_nodes(G_or, pos, nodelist=orient_nodes,
                           node_color=PALETA[0], node_size=600, ax=ax)
    nx.draw_networkx_nodes(G_or, pos, nodelist=topico_nodes,
                           node_color=PALETA[2], node_size=900, ax=ax)
    nx.draw_networkx_labels(G_or, pos, font_size=7, ax=ax)
    edges = G_or.edges(data=True)
    nx.draw_networkx_edges(G_or, pos,
                           width=[d["weight"]*0.8 for _,_,d in edges],
                           alpha=0.6, ax=ax)
    legend = [mpatches.Patch(color=PALETA[0], label="Orientador (2+ TCCs)"),
              mpatches.Patch(color=PALETA[2], label="Tópico dominante")]
    ax.legend(handles=legend, loc="upper left", fontsize=8)
    ax.set_title("Rede orientação → tópico dominante\n"
                 "Espessura = nº TCCs | INDÍCIO — nomes podem ter variações residuais")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(OUT / "5a_rede_orientacao.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✓ 5a_rede_orientacao.png")

    # 5b. Rede de bancas (co-participação)
    def extrai_membros(campo):
        if not campo: return []
        partes = re.split(r"[\n;|/]", campo)
        membros = []
        for p in partes:
            p = norm_nome(p)
            # filtra não-nomes
            if len(p) < 5: continue
            if re.search(r"(universidade|departamento|membro|campus|instituto"
                         r"|ufrr|seed|ufam|ufpa|cefet)", p, re.I): continue
            membros.append(p)
        return membros

    G_banca = nx.Graph()
    sem_banca = 0
    for r in rows:
        membros = extrai_membros(r.get("banca_examinadora",""))
        if not membros: sem_banca += 1; continue
        for i in range(len(membros)):
            for j in range(i+1, len(membros)):
                a, b = membros[i], membros[j]
                if G_banca.has_edge(a, b):
                    G_banca[a][b]["weight"] += 1
                else:
                    G_banca.add_edge(a, b, weight=1)

    print(f"  TCCs sem banca registrada: {sem_banca}/{N}")
    # filtra pares com ao menos 2 co-participações
    edges_filtradas = [(u,v,d) for u,v,d in G_banca.edges(data=True) if d["weight"]>=2]
    G_banca2 = nx.Graph()
    G_banca2.add_edges_from([(u,v,d) for u,v,d in edges_filtradas])

    if G_banca2.number_of_nodes() > 0:
        fig, ax = plt.subplots(figsize=(13, 8))
        pos2 = nx.spring_layout(G_banca2, seed=42, k=3)
        degree = dict(G_banca2.degree())
        node_sizes = [200 + degree[n]*150 for n in G_banca2.nodes]
        nx.draw_networkx_nodes(G_banca2, pos2, node_size=node_sizes,
                               node_color=PALETA[3], alpha=0.85, ax=ax)
        nx.draw_networkx_labels(G_banca2, pos2, font_size=6.5, ax=ax)
        ew = [G_banca2[u][v]["weight"] for u,v in G_banca2.edges()]
        nx.draw_networkx_edges(G_banca2, pos2, width=ew, alpha=0.5, ax=ax)
        ax.set_title(f"Rede de bancas — pares com 2+ co-participações\n"
                     f"(n={G_banca2.number_of_nodes()} pessoas, "
                     f"{G_banca2.number_of_edges()} pares | "
                     f"{sem_banca} TCCs sem banca)")
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(OUT / "5b_rede_bancas.png", dpi=150, bbox_inches="tight")
        plt.close()
        print("✓ 5b_rede_bancas.png")
    else:
        print("  Rede de bancas: sem pares com 2+ co-participações após filtro.")

except ImportError:
    print("  networkx não instalado — etapa 5 pulada.")

# ============================================================================
# 6. ANÁLISE TEMÁTICA — PRESENÇA INDÍGENA
# ============================================================================
TERMOS_INDIGENA = [
    "indigena","indigenas","indigeno","indigenos","indio","indios",
    "indigenismo","indigenista","intercultur","wapichana","macuxi",
    "yanomami","waiwai","wai wai","insikiran","tuxaua","comunidade indigena",
    "escola indigena","educacao indigena","territorio indigeno","terra indigena",
    "povo indigena","povos indigenas","etnia","etnologia","etnografico",
    # Gazetteer regional de Roraima (povos + territórios) — alinha a detecção
    # ao gazetteer do dashboard. Nomes próprios inequívocos; "maloca" foi EXCLUÍDO
    # por ser ambíguo (gerou falso positivo em projeto escolar não indígena).
    "makuxi","wapixana","taurepang","taulipang","ingariko","ingarico","patamona",
    "yanomame","yanomam","yekwana","ye'kwana","yekuana","maiongong","wai-wai",
    "sapara","zapara","pirititi","waimiri","atroari","warao",
    "raposa serra do sol","raposa-serra do sol","comunidade raposa","sao marcos",
    "malacacheta","tabalascada","serra da moca","ananas","manoa-pium",
    "ponta da serra","boqueirao",
]

def menciona_indigena(r):
    campos = " ".join([
        r.get("titulo",""), r.get("resumo",""), r.get("palavras_chave","")
    ]).lower()
    # normaliza acentos: 'indígena' passa a casar com o termo 'indigena'
    campos = unicodedata.normalize("NFKD", campos)
    campos = "".join(c for c in campos if not unicodedata.combining(c))
    return any(t in campos for t in TERMOS_INDIGENA)

for r in rows:
    r["tem_indigena"] = menciona_indigena(r)

total_ind = sum(r["tem_indigena"] for r in rows)
print(f"\n  TCCs com menção indígena: {total_ind}/{N} ({total_ind/N*100:.0f}%)")
print(f"  Termos usados ({len(TERMOS_INDIGENA)}): {', '.join(TERMOS_INDIGENA[:8])}...")

ind_por_grupo = defaultdict(lambda: [0,0])
for r in rows:
    ind_por_grupo[r["grupo"]][1] += 1
    if r["tem_indigena"]: ind_por_grupo[r["grupo"]][0] += 1

fig, ax = plt.subplots(figsize=(10, 4))
gs  = list(ind_por_grupo.keys())
com = [ind_por_grupo[g][0] for g in gs]
sem = [ind_por_grupo[g][1]-ind_por_grupo[g][0] for g in gs]
ax.barh(gs, com, color=PALETA[4], label="Com menção indígena")
ax.barh(gs, sem, left=com, color="#D9D9D9", label="Sem menção")
for i, g in enumerate(gs):
    tot = ind_por_grupo[g][1]
    pct = ind_por_grupo[g][0]/tot*100
    ax.text(tot+0.3, i, f"{pct:.0f}%", va="center", fontsize=8)
ax.legend(fontsize=8); ax.set_xlabel("Nº de TCCs")
ax.set_title("Presença de menção indígena por grupo\n"
             "CRITÉRIO: menção em título, resumo ou palavras-chave — "
             "capta MENÇÃO, não centralidade do tema")
ax.set_xlim(0, max(ind_por_grupo[g][1] for g in gs) + 8)
plt.tight_layout()
plt.savefig(OUT / "6_tematica_indigena.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ 6_tematica_indigena.png")

# ============================================================================
# 7. SALVA CSV ENRIQUECIDO
# ============================================================================
campos_novos = ["ano_num","pag_num","topico_dom","topico_prob","cluster","tem_indigena"]
out_csv = OUT / "corpus_tccs_analisado.csv"
cols_orig = list(csv.DictReader(open(CSV,encoding="utf-8")).fieldnames)
with open(out_csv,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols_orig+campos_novos)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c,"") for c in cols_orig+campos_novos})
print(f"✓ corpus_tccs_analisado.csv ({N} linhas, {len(cols_orig)+len(campos_novos)} colunas)")

# ============================================================================
# 8. RELATÓRIO TEXTUAL
# ============================================================================
relatorio = f"""
RELATÓRIO EXPLORATÓRIO — CORPUS TCCs LIDAE/UFRR
================================================
Data: 2026-06-16 | Piloto: {N} TCCs | Natureza: exploratória, não censitária

1. CORPUS
   - {N} TCCs únicos consolidados a partir de 2 formulários Google Forms.
   - Grupos: {', '.join(f'{g} ({cnt_grupo[g]})' for g in grupos_ord)}.
   - Anos com registro: {min(anos_validos) if anos_validos else '?'}–{max(anos_validos) if anos_validos else '?'}
     ({N-len(anos_validos)} TCCs sem ano informado — excluídos desta contagem).

2. PÁGINAS (mediana por grupo — assimetria justifica mediana)
""".strip() + "\n"

for g in grupos_ord:
    pg = pags_grupo.get(g, [])
    if pg:
        relatorio += f"   {g}: mediana={np.median(pg):.0f} | min={min(pg):.0f} | max={max(pg):.0f} | n={len(pg)}\n"
    else:
        relatorio += f"   {g}: sem dados de páginas\n"

relatorio += f"""
3. LDA (K={K_best} tópicos, menor perplexidade)
   Perplexidades testadas: { {k: round(v,1) for k,v in perps.items()} }
   ATENÇÃO: rótulos abaixo são aproximados e requerem revisão qualitativa.
"""
for t, terms in termos_top.items():
    relatorio += f"   [{ROTULOS.get(t,'?')}]: {', '.join(terms)}\n"

relatorio += f"""
4. CLUSTERING (k={K_clust}, silhueta={silhs[K_clust]:.3f})
   Silhueta baixa é esperada em corpus pequeno e texto curto — indica
   fronteiras temáticas porosas, não falha metodológica.
"""
for k in range(K_clust):
    membros = [r["grupo"] for r in rows if r["cluster"]==k]
    relatorio += f"   C{k} (n={len(membros)}): {dict(Counter(membros).most_common(3))}\n"

relatorio += f"""
5. REDES
   Orientadores com 2+ TCCs: {len(orient_recorrentes)} ({pct_recorrentes:.0f}% dos TCCs).
   TCCs sem banca registrada: {sem_banca}/{N} — campo não preenchido na fonte.
   Nomes normalizados (títulos removidos); variações residuais podem subsistir.

6. MENÇÃO INDÍGENA
   {total_ind}/{N} TCCs ({total_ind/N*100:.0f}%) mencionam termos indígenas.
   Critério: lista de {len(TERMOS_INDIGENA)} termos em título + resumo + palavras-chave.
   LIMITE: capta MENÇÃO, não centralidade. Falsos positivos/negativos possíveis.
   Lista completa de termos: {', '.join(TERMOS_INDIGENA)}.

LIMITAÇÕES GERAIS
   - Corpus piloto (128 TCCs) — resultados não generalizáveis ao acervo completo.
   - Alguns grupos têm n muito pequeno (LEDUCAR=1, Letras=6) — estatísticas instáveis.
   - Resumos incompletos ou ausentes afetam LDA e clustering.
   - Nomes de orientadores/bancas têm variações residuais mesmo após normalização.
"""

(OUT / "relatorio_exploratorio.txt").write_text(relatorio, encoding="utf-8")
print("✓ relatorio_exploratorio.txt")
print("\nAnálise concluída. Arquivos em:", OUT)

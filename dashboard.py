#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard interativo — Corpus de TCCs das Licenciaturas UFRR (LIDAE)
Executar:  streamlit run dashboard.py

Princípios (CLAUDE.md): exploratório (não censitário), mediana p/ páginas,
nunca imputar, sempre declarar denominador e exclusões, indício ≠ conclusão.
"""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from rapidfuzz import fuzz  # wheels pré-compilados (substitui fuzzywuzzy+Levenshtein)
import re, unicodedata, json
from streamlit_option_menu import option_menu
import plotly.io as pio

# ─────────────────────────────────────────────────────────────────────────────
# FONTE PADRÃO — Source Sans Pro (padrão do Streamlit), aplicada à interface
# (CSS) e aos gráficos (Plotly). Mantém o mesmo tipo em todo o dashboard.
# (No Google Fonts a família atual chama-se "Source Sans 3".)
# ─────────────────────────────────────────────────────────────────────────────
FONTE = "'Source Sans Pro', 'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
# (o template "necpf" definido após a PALETA aplica a fonte aos gráficos)

# ─────────────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
CSV = BASE / "outputs" / "analise" / "corpus_tccs_analisado.csv"

# ─────────────────────────────────────────────────────────────────────────────
# PALETA DE CORES — Identidade Visual NECPF
# ─────────────────────────────────────────────────────────────────────────────
# Verde-floresta (institucional), Azul-teal, Âmbar, Terracota
PALETA = ["#1B5E3B",   # Verde-floresta (1)
          "#1A7A8A",   # Azul-teal (2)
          "#D4A017",   # Âmbar (3)
          "#C1440E",   # Terracota (4)
          "#468A66",   # Verde médio (5)
          "#5FA9B5",   # Teal claro (6)
          "#88660E",   # Âmbar profundo (7)
          "#DF7B53"]   # Terracota clara (8)

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE PLOTLY "NECPF" — aplica a identidade visual aos gráficos:
# paleta categórica (§5.1), escala sequencial verde (§5.2), divergente (§5.3),
# fundo transparente, grades/eixos em neutros, títulos em verde-floresta, fonte.
# Combinado com o template base ("plotly+necpf") p/ herdar bons padrões.
# ─────────────────────────────────────────────────────────────────────────────
SEQ_NECPF = ["#E8F1EC", "#9FC6AE", "#468A66", "#1B5E3B", "#103A25"]   # sequencial §5.2
DIV_NECPF = ["#7C2C09", "#D45D2E", "#FBEAE3", "#93C6CE", "#114E5A"]   # divergente §5.3
CINZA_NEUTRO = "#DEE1DB"   # neutro-200 (ex.: categoria "sem menção")

def _escala(cores):
    n = len(cores)
    return [[i / (n - 1), c] for i, c in enumerate(cores)]

_necpf = go.layout.Template()
_necpf.layout = go.Layout(
    font=dict(family=FONTE, color="#363A33", size=13),       # neutro-700
    title=dict(font=dict(family=FONTE, color="#1B5E3B")),    # verde-floresta
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=PALETA,                                         # categórica §5.1
    xaxis=dict(gridcolor=CINZA_NEUTRO, linecolor="#C2C7BE",
               zerolinecolor=CINZA_NEUTRO, tickfont=dict(color="#4E534A")),
    yaxis=dict(gridcolor=CINZA_NEUTRO, linecolor="#C2C7BE",
               zerolinecolor=CINZA_NEUTRO, tickfont=dict(color="#4E534A")),
    legend=dict(font=dict(family=FONTE, color="#363A33")),
    colorscale=dict(sequential=_escala(SEQ_NECPF),
                    diverging=_escala(DIV_NECPF)),
)
pio.templates["necpf"] = _necpf
pio.templates.default = "plotly+necpf"

# ─────────────────────────────────────────────────────────────────────────────
# HABILITAÇÕES — só os cursos AGREGADOS em grupo_tcc (Insikiran, Letras) têm
# sub-habilitação distinta nos TCCs (CLAUDE.md §5). Mapeia curso_fonte → rótulo;
# os demais cursos permanecem pelo grupo_tcc.
# ─────────────────────────────────────────────────────────────────────────────
SPLIT_HABILITACAO = {
    "Insikiran – Ciências da Natureza": "Insikiran — Ciências da Natureza",
    "Insikiran – Ciências Sociais":     "Insikiran — Ciências Sociais",
    "Insikiran – Comunicação e Artes":  "Insikiran — Comunicação e Artes",
    "Letras – Inglês":                  "Letras — Inglês (nova estrutura)",
    "Letras – Português":               "Letras — Português (nova estrutura)",
    "Letras – Curso anterior":          "Letras — Hab. Literatura/Português (antiga)",
}

def curso_habilitacao(row):
    """Rótulo de curso desagregado por habilitação (só Insikiran e Letras)."""
    if row["grupo_tcc"] in ("Insikiran", "Letras"):
        return SPLIT_HABILITACAO.get(row["curso_fonte"], row["grupo_tcc"])
    return row["grupo_tcc"]

# ─────────────────────────────────────────────────────────────────────────────
# NORMALIZAÇÃO DE NOMES (orientadores e pesquisadores)
# ─────────────────────────────────────────────────────────────────────────────
def limpa_nome(s):
    """Remove títulos, diacríticos, pontuação; retorna nome limpo (title case)."""
    s = str(s or "").strip()
    # remove pontuação no final
    s = s.rstrip(".,;:")
    # remove parênteses e conteúdo
    s = re.sub(r"\([^)]*\)", "", s)
    # remove sequências de instituições (Universidade..., UFRR, UFAM, etc. no final com vírgula antes)
    s = re.sub(r",\s*(?:Universidade|Federal|Instituto|UFRR|UFAM|SEED|Curso|Departamento).*$", "", s, flags=re.I)
    # remove títulos académicos
    s = re.sub(r"\b(Prof|Profa|Professor|Professora|Dr|Dra|Doutor|Doutora|"
                r"Me|Msc|Mestrado|Ms|Mestre|Esp|Ph\.?D|PhD|MSc|Ma|Pós-doutor)\b\.?\s*",
                "", s, flags=re.I)
    # remove "em Educação" e similares no final
    s = re.sub(r"\s+(?:em|de Educação|de Educación|de Estudo).*$", "", s, flags=re.I)
    # remove diacríticos
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # remove TODOS os pontos (incluindo iniciais de nomes: J.C. → JC)
    s = s.replace(".", " ")
    # remove pontuação exceto espaço
    s = re.sub(r"[^\w\s]", " ", s)
    # colapsa espaços
    s = re.sub(r"\s+", " ", s).strip()
    # capitaliza (Title Case)
    s = " ".join(w.capitalize() for w in s.split() if w)
    return s

def norm_nome_agressiva(s):
    """Normaliza para fuzzy matching (uppercase, sem diacríticos)."""
    s = limpa_nome(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.upper()

def consolida_nomes(nomes_list, threshold=85):
    """Agrupa nomes semelhantes (fuzzy matching) e retorna mapa original→canônico."""
    nomes = [n for n in nomes_list if n and len(str(n).strip()) > 3]
    nomes = list(set(nomes))  # únicos
    nomes.sort(key=len, reverse=True)  # maiores primeiro (nomes mais completos)

    mapa = {}
    usados = set()

    for n in nomes:
        if n in usados:
            continue
        nor = norm_nome_agressiva(n)
        if nor in usados:
            continue
        grupo = [n]
        usados.add(n)
        # procura outros nomes similares
        for m in nomes:
            if m in usados or m == n:
                continue
            nor_m = norm_nome_agressiva(m)
            if fuzz.token_sort_ratio(nor, nor_m) >= threshold:
                grupo.append(m)
                usados.add(m)
        # usa o primeiro (mais completo) como canônico
        canonico = grupo[0]
        for nm in grupo:
            mapa[nm] = canonico

    return mapa

# Rótulos LDA — APROXIMADOS, derivados dos 10 termos mais prováveis.
# Edite as leituras conforme revisão qualitativa.
# Atualizado com K=4 (145 TCCs, após consolidar 2 duplicatas) — rótulos PROVISÓRIOS.
TOPICOS = {
    0: {"rotulo": "Música, estágio e prática pedagógica (provisório)",
        "leitura": "educação musical, estágio, experiência e prática docente",
        "termos": "educacao, pedagogica, estagio, musica, roraima, musical, "
                  "pratica, experiencia, coordenacao, vista"},
    1: {"rotulo": "Educação e contextos escolares — difuso (provisório)",
        "leitura": "tópico heterogêneo (música, escolas, dados/contexto)",
        "termos": "educacao, contexto, vista, tambem, dados, musica, roraima, "
                  "alem, importancia, escolas"},
    2: {"rotulo": "Matemática — Teoria Histórico-Cultural (provisório)",
        "leitura": "atividade de situações-problema, Galperin, resolução",
        "termos": "atividade, problema, matematica, educacao, situacoes, "
                  "formacao, teoria, estudantes, resolucao, acoes"},
    3: {"rotulo": "Educação escolar indígena (provisório)",
        "leitura": "comunidade, cultura, língua, leitura, saberes indígenas",
        "termos": "indigena, comunidade, indigenas, estadual, proposta, leitura, "
                  "lingua, conhecimentos, cultura, educacao"},
}

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="TCCs Licenciaturas UFRR — LIDAE",
                   page_icon="📚", layout="wide")

# Fonte única (Source Sans Pro) em toda a interface — títulos, textos, tabelas,
# sidebar, menu de navegação, widgets. Os gráficos Plotly usam a mesma via template.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');
html, body, [class*="css"], [class*="st-"], .stApp, .stMarkdown,
.stDataFrame, .stMetric, button, input, select, textarea,
[data-testid="stSidebar"], [data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    font-family: 'Source Sans Pro', 'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar():
    df = pd.read_csv(CSV)
    df["ano_num"] = pd.to_numeric(df["ano_num"], errors="coerce")
    df["pag_num"] = pd.to_numeric(df["pag_num"], errors="coerce")
    df["tem_indigena"] = df["tem_indigena"].astype(str).str.lower().isin(
        ["true", "1", "sim", "verdadeiro"])
    df["topico_dom"] = pd.to_numeric(df["topico_dom"], errors="coerce")

    # LIMPA orientadores: remove títulos (Prof., Dr., etc.) e pontos
    df["orientador"] = df["orientador"].apply(lambda x: limpa_nome(x) if pd.notna(x) else x)
    # consolida nomes de orientadores (threshold mais alto = mais conservador)
    mapa_orient = consolida_nomes(df["orientador"].dropna().unique(), threshold=85)
    df["orientador"] = df["orientador"].map(lambda x: mapa_orient.get(x, x) if pd.notna(x) else x)

    # LIMPA pesquisadores: remove pontos e variações
    df["pesquisador"] = df["pesquisador"].apply(lambda x: limpa_nome(x) if pd.notna(x) else x)
    # consolida nomes de pesquisadores (threshold mais baixo = mais permissivo para variações)
    mapa_pesq = consolida_nomes(df["pesquisador"].dropna().unique(), threshold=78)
    df["pesquisador"] = df["pesquisador"].map(lambda x: mapa_pesq.get(x, x) if pd.notna(x) else x)

    return df


@st.cache_data
def carregar_por_curso():
    """Lê o JSON gerado por analise_por_curso.py (fonte única). None se ausente."""
    p = BASE / "outputs" / "analise" / "analise_por_curso.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


df = carregar()
N_TOTAL = len(df)

# curso desagregado por habilitação (Insikiran e Letras); usado em filtros e gráficos
df["curso_det"] = df.apply(curso_habilitacao, axis=1)

# ─────────────────────────────────────────────────────────────────────────────
# ORDEM CANÔNICA DE CURSOS — fixa em TODO o dashboard: por nº de TCCs (desc).
# Evita que cada gráfico/lista organize os cursos de forma diferente.
# ─────────────────────────────────────────────────────────────────────────────
ORDEM_CURSOS = df["grupo_tcc"].value_counts().index.tolist()
ORDEM_CURSOS_DET = df["curso_det"].value_counts().index.tolist()  # nível habilitação

# rótulos de coluna para as listagens
ROTULOS_COLS = {
    "id": "id", "grupo_tcc": "Curso", "curso_det": "Curso",
    "titulo": "Título", "autor": "Autor",
    "orientador": "Orientador", "pesquisador": "Pesquisador",
    "ano_num": "Ano", "pag_num": "Páginas", "topico_rotulo": "Tópico",
    "tem_indigena": "Menção indígena",
}


def lista_tccs(dados, key, cols):
    """Lista de TCCs com controles de ORDENAÇÃO e seleção de colunas.
    Ordenar por 'Curso' respeita a ordem canônica (nº de TCCs desc)."""
    if dados.empty:
        st.info("Nenhum TCC para listar com os filtros atuais.")
        return
    cset = [c for c in cols if c in dados.columns]
    c1, c2, c3 = st.columns([2, 1, 3])
    ordenar = c1.selectbox("Ordenar por", cset, key=f"{key}_s",
                           format_func=lambda c: ROTULOS_COLS.get(c, c))
    asc = c2.radio("Direção", ["crescente", "decrescente"], key=f"{key}_d",
                   horizontal=True) == "crescente"
    mostrar = c3.multiselect("Colunas exibidas", cset, default=cset,
                             key=f"{key}_c",
                             format_func=lambda c: ROTULOS_COLS.get(c, c)) or cset

    d = dados.copy()
    if ordenar in ("grupo_tcc", "curso_det"):
        ordem = ORDEM_CURSOS_DET if ordenar == "curso_det" else ORDEM_CURSOS
        d["_o"] = pd.Categorical(d[ordenar], categories=ordem, ordered=True)
        d = d.sort_values(["_o", "id"], ascending=[asc, True]).drop(columns="_o")
    else:
        d = d.sort_values(ordenar, ascending=asc, na_position="last")

    # Ano/páginas como texto puro → sem separador de milhar (ex.: 2023, não 2.023)
    for c in ("ano_num", "pag_num"):
        if c in d.columns:
            d[c] = d[c].apply(lambda x: "" if pd.isna(x) else str(int(x)))
    st.caption(f"{len(d)} TCCs.")
    st.dataframe(d[mostrar].rename(columns=ROTULOS_COLS),
                 use_container_width=True, hide_index=True, height=340)


# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("📚 Corpus de TCCs — Licenciaturas UFRR")
st.caption("Laboratório de Indicadores, Dados e Analítica Educacional · LIDAE/NECPF · "
           "Piloto exploratório")
st.info("⚠️ **Análise exploratória, não censitária.** Cada número é indício a "
        "interpretar, não conclusão. Corpus-piloto desbalanceado — grupos com "
        "poucos TCCs (LEDUCAR, Letras) têm estatísticas instáveis.", icon="⚠️")

# ── Navegação (menu lateral com ícones) ──
SECOES = ["Distribuição", "Tópicos (LDA)", "Por curso", "Menção indígena",
          "Orientadores", "Explorar TCCs", "Cobertura de Coleta"]
with st.sidebar:
    secao = option_menu(
        "Navegação", SECOES,
        icons=["bar-chart-line", "diagram-3", "mortarboard", "feather",
               "people", "search", "graph-up-arrow"],
        menu_icon="compass", default_index=0,
        styles={
            # Identidade NECPF: fundo neutro, ícone âmbar (contrasta no claro e no
            # verde selecionado), item selecionado verde-floresta c/ texto branco.
            "container": {"padding": "5px", "background-color": "#F7F8F6"},
            "icon": {"color": "#D4A017", "font-size": "16px"},
            "menu-title": {"color": "#1B5E3B", "font-weight": "600"},
            "nav-link": {"font-size": "14px", "color": "#363A33",
                         "text-align": "left", "--hover-color": "#E3ECE6"},
            "nav-link-selected": {"background-color": "#1B5E3B", "color": "white"},
        })

# ── Sidebar: filtros ─────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
sel_grupos = st.sidebar.multiselect("Curso (com habilitações)", ORDEM_CURSOS_DET,
                                    default=ORDEM_CURSOS_DET)

anos_validos = df["ano_num"].dropna()
if not anos_validos.empty:
    amin, amax = int(anos_validos.min()), int(anos_validos.max())
    sel_anos = st.sidebar.slider("Ano de defesa", amin, amax, (amin, amax))
else:
    sel_anos = None

so_indigena = st.sidebar.checkbox("Apenas com menção indígena")
incluir_sem_ano = st.sidebar.checkbox("Incluir TCCs sem ano informado",
                                      value=True)

# aplica filtros (curso desagregado por habilitação)
f = df[df["curso_det"].isin(sel_grupos)].copy()
if sel_anos:
    mask_ano = f["ano_num"].between(*sel_anos)
    if incluir_sem_ano:
        mask_ano = mask_ano | f["ano_num"].isna()
    f = f[mask_ano]
if so_indigena:
    f = f[f["tem_indigena"]]

st.sidebar.markdown("---")
st.sidebar.metric("TCCs no filtro", f"{len(f)} / {N_TOTAL}")
st.sidebar.caption("Os números abaixo recalculam conforme o filtro. "
                   "Denominador = TCCs selecionados.")

if f.empty:
    st.warning("Nenhum TCC com os filtros atuais.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("TCCs", len(f))
c2.metric("Grupos", f["grupo_tcc"].nunique())
med_pag = f["pag_num"].median()
c3.metric("Mediana de páginas", f"{med_pag:.0f}" if pd.notna(med_pag) else "—",
          help="Mediana (não média) — distribuição assimétrica. "
               f"Exclui {f['pag_num'].isna().sum()} sem dado.")
pct_ind = f["tem_indigena"].mean() * 100
c4.metric("Menção indígena", f"{pct_ind:.0f}%",
          help="Menção em título, resumo ou palavras-chave. Capta MENÇÃO, "
               "não centralidade do tema.")
def tem_banca(s):
    s = str(s).strip()
    return s not in ("", "nan", "Não informado", "Não se aplica", "Não")
pct_banca = f["banca_examinadora"].apply(tem_banca).mean() * 100
c5.metric("Com banca registrada", f"{pct_banca:.0f}%",
          help="Campo vindo das fontes; ausência = lacuna de coleta, "
               "não inexistência de banca.")
n_pesq = f["pesquisador"].nunique()
c6.metric("Pesquisadores", n_pesq,
          help="Nº de pessoas que catalogaram os TCCs neste filtro.")

st.markdown("---")

# ── Abas ─────────────────────────────────────────────────────────────────────
# Conteúdo de cada seção é escolhido pelo menu lateral (secao)

# Aba 1 — Distribuição
if secao == SECOES[0]:
    st.subheader("TCCs por curso (com habilitações)")
    st.caption("Insikiran e Letras aparecem desagregados por habilitação; "
               "os demais cursos não têm sub-habilitação no corpus.")
    fcd = f.copy()
    fcd["curso_det"] = fcd.apply(curso_habilitacao, axis=1)
    vc = fcd["curso_det"].value_counts().reset_index()
    vc.columns = ["grupo", "n"]
    fig = px.bar(vc, x="n", y="grupo", orientation="h",
                 text="n", color="grupo",
                 color_discrete_sequence=PALETA)
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"},
                      xaxis_title="Nº de TCCs", yaxis_title="",
                      height=max(380, len(vc) * 36))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("TCCs por ano de defesa")
    anos = f.dropna(subset=["ano_num"])
    n_sem = f["ano_num"].isna().sum()
    if not anos.empty:
        ano_ini = 2015                       # piso do eixo (janela 2015–atual, CLAUDE.md §4)
        ano_atual = pd.Timestamp.now().year
        anos_int = anos["ano_num"].astype(int)
        n_fora = int(((anos_int < ano_ini) | (anos_int > ano_atual)).sum())
        # eixo FIXO de ano_ini ao ano atual; anos sem TCC = 0
        serie = (anos_int[(anos_int >= ano_ini) & (anos_int <= ano_atual)]
                 .value_counts().sort_index()
                 .reindex(range(ano_ini, ano_atual + 1), fill_value=0))
        va = serie.reset_index()
        va.columns = ["ano", "n"]
        va["rotulo"] = va["n"].apply(lambda x: str(int(x)) if x > 0 else "")
        fig = px.bar(va, x="ano", y="n", text="rotulo",
                     color_discrete_sequence=[PALETA[0]])
        fig.update_layout(xaxis_title="Ano", yaxis_title="Nº de TCCs",
                          height=380)
        fig.update_xaxes(tickmode="linear", tick0=ano_ini, dtick=1, tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        if n_fora:
            st.caption(f"⚠️ {n_fora} TCC(s) com ano fora de {ano_ini}–{ano_atual} "
                       "(provável erro de registro) — excluído(s) do gráfico; verificar.")
    st.caption(f"⚠️ {n_sem} TCCs sem ano informado — excluídos deste gráfico "
               "(não imputados).")
    st.caption("A curva NÃO deve ser lida como 'aumento de produção docente' "
               "— reflete disponibilidade do acervo digitalizado.")

    st.subheader("Páginas por curso (mediana)")
    st.caption("Agrupado por curso/habilitação — fonte: coluna `curso_fonte` "
               "(Insikiran e Letras desagregados). Mediana, não média (CLAUDE.md §7).")
    pgd = fcd.dropna(subset=["pag_num"])
    if not pgd.empty:
        ordem_det = pgd["curso_det"].value_counts().index.tolist()
        fig = px.box(pgd, x="pag_num", y="curso_det", color="curso_det",
                     color_discrete_sequence=PALETA, points="all",
                     category_orders={"curso_det": ordem_det[::-1]})
        fig.update_layout(showlegend=False, xaxis_title="Páginas", yaxis_title="",
                          height=max(400, len(ordem_det) * 42))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Exclui {f['pag_num'].isna().sum()} TCCs sem nº de páginas. "
                   "Habilitações de Letras têm poucos TCCs (n=1–3) — leitura cautelosa.")

    st.markdown("---")
    st.markdown("#### 📋 Lista de TCCs (por curso)")
    lista_tccs(f, key="dist",
               cols=["id", "curso_det", "titulo", "autor", "ano_num",
                     "pag_num", "pesquisador"])

# Aba 2 — Tópicos LDA
if secao == SECOES[1]:
    st.subheader("Distribuição de tópicos (modelagem LDA, K=4)")
    st.caption("⚠️ Rótulos APROXIMADOS, derivados dos termos mais prováveis. "
               "Tópico ≠ categoria sociológica; requer revisão qualitativa.")
    fdt = f.dropna(subset=["topico_dom"]).copy()
    fdt["topico_rotulo"] = fdt["topico_dom"].map(
        lambda i: TOPICOS.get(int(i), {}).get("rotulo", f"Tópico {int(i)}"))

    cc1, cc2 = st.columns([2, 3])
    with cc1:
        vt = fdt["topico_rotulo"].value_counts().reset_index()
        vt.columns = ["topico", "n"]
        fig = px.pie(vt, names="topico", values="n", hole=0.45,
                     color_discrete_sequence=PALETA)
        fig.update_layout(height=380, legend_title="Tópico dominante")
        st.plotly_chart(fig, use_container_width=True)
    with cc2:
        st.markdown("**Tópico dominante × grupo de curso**")
        ct = pd.crosstab(fdt["topico_rotulo"], fdt["grupo_tcc"])
        ct = ct[[c for c in ORDEM_CURSOS if c in ct.columns]]  # ordem canônica
        fig = px.imshow(ct, text_auto=True, color_continuous_scale=SEQ_NECPF,
                        aspect="auto")
        fig.update_layout(height=380, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Termos mais prováveis por tópico** (revisar leituras)")
    for i, info in TOPICOS.items():
        st.markdown(f"- **{info['rotulo']}** — _{info['leitura']}_  \n"
                    f"  <span style='color:gray;font-size:0.85em'>{info['termos']}</span>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 Lista de TCCs (por tópico)")
    topos = ["(todos)"] + [TOPICOS.get(int(i), {}).get("rotulo", f"Tópico {int(i)}")
                           for i in sorted(fdt["topico_dom"].dropna().unique())]
    sel_topico = st.selectbox("Filtrar por tópico dominante", topos, key="lda_filtro")
    flt = fdt if sel_topico == "(todos)" else fdt[fdt["topico_rotulo"] == sel_topico]
    lista_tccs(flt, key="lda",
               cols=["id", "curso_det", "topico_rotulo", "titulo", "autor", "ano_num"])

    # ── Metodologia (integrada à aba de Tópicos)
    st.markdown("---")
    st.subheader("📖 Como descubrimos os 'assuntos' dos TCCs: a técnica LDA")
    st.markdown("""
    #### A pergunta de partida
    Temos mais de uma centena de trabalhos de conclusão de curso (TCCs) das licenciaturas da UFRR.
    Lê-los um a um, classificando seus temas à mão, seria lento e sujeito ao olhar de quem classifica.
    Existe uma forma de o computador sugerir, sozinho, sobre quais assuntos esses trabalhos falam?
    **Existe — e uma das técnicas mais usadas para isso chama-se LDA.**

    #### A ideia, em uma frase
    A LDA parte de uma suposição simples e intuitiva:
    **todo texto fala de mais de um assunto ao mesmo tempo, em proporções diferentes**.
    Um TCC pode ser, digamos, 70% sobre cultura e saberes tradicionais e 30% sobre material didático;
    outro pode misturar esses mesmos temas em proporção inversa.

    A partir das palavras que efetivamente aparecem nos trabalhos, o algoritmo faz duas coisas ao mesmo tempo:

    - Agrupa palavras que costumam aparecer juntas, formando **temas** (por exemplo, um conjunto onde
    *língua, cultura, comunidade e escola* têm peso alto).
    - Estima a **proporção de cada tema** dentro de cada TCC.

    É como observar muitas receitas sem conhecer os pratos e, só pelos ingredientes que se repetem,
    deduzir que existem "receitas de bolo", "de sopa" e "de salada" — e depois dizer quanto de cada
    estilo há em cada prato.

    #### Um cuidado essencial
    O computador entrega **listas de palavras**, não rótulos prontos. Quem dá o nome "cultura e
    interculturalidade" a um conjunto de palavras é o pesquisador, depois de olhar o resultado.
    Mais importante: a técnica identifica **quais palavras aparecem com frequência**, e não necessariamente
    qual é o foco central do trabalho. Um TCC pode citar "indígena" de passagem sem que esse seja seu tema principal.

    Por isso, no LIDAE, o resultado da LDA é tratado como **indício, um ponto de partida para a leitura** —
    nunca como conclusão definitiva. A interpretação final exige a leitura cuidadosa dos textos pelos pesquisadores.

    #### Em resumo
    A LDA não substitui o olhar humano: ela organiza o material e aponta padrões que mereceriam,
    de outro modo, semanas de leitura manual. O computador sugere os caminhos; a interpretação
    continua sendo nossa.

    ---

    **Princípio metodológico:**
    *Métodos computacionais como instrumentos de leitura, não como veredito.*

    *Laboratório de Indicadores, Dados e Analítica Educacional — LIDAE/NECPF–UFRR*
    """)

# Aba 3 — Por curso (análise temática em camadas)
if secao == SECOES[2]:
    st.subheader("Análise temática por curso (em camadas)")
    st.caption("O LDA global apenas separa os cursos entre si; aqui olhamos "
               "DENTRO de cada curso. O método se ajusta ao Nº de TCCs: "
               "🟢 LDA (sub-temas) · 🟠 descritivo (termos + leitura) · "
               "🔴 listagem. Exploratório, não censitário (CLAUDE.md §1, §4).")

    PC = carregar_por_curso()
    if PC is None:
        st.warning("Análise por curso ainda não gerada. "
                   "Rode no terminal: `python3 analise_por_curso.py`")
    else:
        cursos = PC["cursos"]
        rotulo = {"lda": "🟢 LDA — sub-temas",
                  "descritivo": "🟠 Descritivo — termos + leitura",
                  "listagem": "🔴 Listagem — sem modelagem"}
        nomes = [f"{c['curso']} · {c['n']} TCCs · {c['camada']}" for c in cursos]
        idx = st.selectbox("Selecione o curso", range(len(cursos)),
                           format_func=lambda i: nomes[i])
        c = cursos[idx]

        st.markdown(f"#### {c['curso']} — {c['n']} TCCs · {rotulo[c['camada']]}")

        if c["camada"] == "lda":
            K, ari = c["lda"]["K"], c["lda"]["ari"]
            st.caption(f"LDA dentro do curso · K={K} escolhido por estabilidade "
                       f"(ARI={ari:.2f} entre 8 seeds).")
            if ari < 0.4:
                st.warning(f"⚠️ Estabilidade baixa (ARI={ari:.2f}): os sub-temas "
                           "são INDÍCIO frágil — fronteiras porosas entre eles, "
                           "não categorias fechadas. Confirmar por leitura.")
            for n, sub in enumerate(c["lda"]["subtemas"], 1):
                st.markdown(
                    f"**Sub-tema {n}** ({sub['n']} TCCs)  \n"
                    f"<span style='color:gray;font-size:0.9em'>"
                    f"{', '.join(sub['termos'])}</span>",
                    unsafe_allow_html=True)
                for e in sub["exemplos"]:
                    st.markdown(f"&nbsp;&nbsp;◦ *id {e['id']}* ({e['ano']}): "
                                f"{e['titulo']}", unsafe_allow_html=True)
            st.markdown("---")
        elif c["camada"] == "descritivo":
            st.caption("N insuficiente para LDA confiável. Mostram-se os termos "
                       "mais recorrentes (em nº de TCCs) e a lista de trabalhos — "
                       "modelar tópicos aqui seria ruído.")
        elif c["camada"] == "listagem":
            st.caption(f"N ínfimo ({c['n']}): qualquer modelagem seria artefato "
                       "(CLAUDE.md §1). Apenas identificação dos trabalhos.")

        # termos recorrentes (camadas LDA e descritiva)
        if c["top_termos"]:
            td = pd.DataFrame(c["top_termos"], columns=["termo", "n"])
            fig = px.bar(td.sort_values("n"), x="n", y="termo", orientation="h",
                         text="n", color_discrete_sequence=[PALETA[1]])
            fig.update_layout(showlegend=False, height=max(280, len(td) * 26),
                              xaxis_title="Nº de TCCs em que o termo aparece",
                              yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        # lista de trabalhos do curso
        st.markdown("**Trabalhos do curso:**")
        tdf = pd.DataFrame(c["tccs"]).rename(
            columns={"id": "id", "ano": "Ano", "titulo": "Título"})
        st.dataframe(tdf, use_container_width=True, hide_index=True, height=260)

# Aba 4 — Menção indígena
if secao == SECOES[3]:
    st.subheader("Presença de menção indígena por grupo")
    st.caption("CRITÉRIO: lista de 26 termos (indígena, intercultural, macuxi, "
               "wapichana, wai wai, terra indígena…) buscada em título + resumo "
               "+ palavras-chave. Capta MENÇÃO, não centralidade. Sujeito a "
               "falsos positivos/negativos.")
    g = f.groupby("grupo_tcc")["tem_indigena"].agg(["sum", "count"]).reset_index()
    g["_o"] = pd.Categorical(g["grupo_tcc"], categories=ORDEM_CURSOS, ordered=True)
    g = g.sort_values("_o").drop(columns="_o")
    g["com"] = g["sum"].astype(int)
    g["sem"] = g["count"] - g["com"]
    g["pct"] = (g["com"] / g["count"] * 100).round(0)
    fig = go.Figure()
    fig.add_bar(y=g["grupo_tcc"], x=g["com"], orientation="h",
                name="Com menção", marker_color=PALETA[4])
    fig.add_bar(y=g["grupo_tcc"], x=g["sem"], orientation="h",
                name="Sem menção", marker_color=CINZA_NEUTRO)
    fig.update_layout(barmode="stack", height=380, xaxis_title="Nº de TCCs",
                      yaxis_title="", legend_title="",
                      yaxis={"categoryorder": "array",
                             "categoryarray": ORDEM_CURSOS[::-1]})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        g[["grupo_tcc", "com", "count", "pct"]].rename(
            columns={"grupo_tcc": "Grupo", "com": "Com menção",
                     "count": "Total", "pct": "% menção"}),
        use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📋 Lista de TCCs (por menção indígena)")
    op = st.radio("Filtrar", ["Todos", "Só com menção", "Só sem menção"],
                  horizontal=True, key="ind_filtro")
    flt = f
    if op == "Só com menção":
        flt = f[f["tem_indigena"]]
    elif op == "Só sem menção":
        flt = f[~f["tem_indigena"]]
    lista_tccs(flt, key="ind",
               cols=["id", "curso_det", "tem_indigena", "titulo", "autor", "ano_num"])

# Aba 5 — Orientadores
if secao == SECOES[4]:
    st.subheader("Orientadores recorrentes")
    st.caption("Nomes consolidados por fuzzy matching (similitude ≥85%). "
               "Variações de grafia foram agrupadas sob o nome mais completo.")
    vo = f[f["orientador"].str.len() > 4]["orientador"].value_counts()
    vo = vo[vo >= 2].reset_index()
    vo.columns = ["orientador", "n"]
    if not vo.empty:
        pct = vo["n"].sum() / len(f) * 100
        st.metric("Concentração", f"{pct:.0f}% dos TCCs",
                  help="% de TCCs sob orientadores com 2+ trabalhos no filtro.")
        fig = px.bar(vo, x="n", y="orientador", orientation="h", text="n",
                     color_discrete_sequence=[PALETA[1]])
        fig.update_layout(showlegend=False, height=max(300, len(vo)*32),
                          yaxis={"categoryorder": "total ascending"},
                          xaxis_title="TCCs orientados", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nenhum orientador com 2+ TCCs no filtro atual.")

    st.markdown("---")
    st.markdown("#### 📋 Lista de TCCs (por orientador)")
    orientadores = ["(todos)"] + sorted(
        f[f["orientador"].str.len() > 4]["orientador"].dropna().unique())
    sel_o = st.selectbox("Filtrar por orientador", orientadores, key="ori_filtro")
    flt = f if sel_o == "(todos)" else f[f["orientador"] == sel_o]
    lista_tccs(flt, key="ori",
               cols=["id", "curso_det", "orientador", "titulo", "autor", "ano_num"])

# Aba 6 — Explorar
if secao == SECOES[5]:
    st.subheader("Explorador de TCCs")
    busca = st.text_input("Buscar em título / resumo / palavras-chave")
    fe = f.copy()
    if busca:
        b = busca.lower()
        mask = (fe["titulo"].str.lower().str.contains(b, na=False) |
                fe["resumo"].str.lower().str.contains(b, na=False) |
                fe["palavras_chave"].str.lower().str.contains(b, na=False))
        fe = fe[mask]
    lista_tccs(fe, key="expl",
               cols=["id", "curso_det", "titulo", "autor", "orientador",
                     "pesquisador", "ano_num", "pag_num"])
    with st.expander("Ver resumo completo de um TCC"):
        if not fe.empty:
            tid = st.selectbox("Selecione o id", fe["id"].tolist())
            row = fe[fe["id"] == tid].iloc[0]
            st.markdown(f"**{row['titulo']}**")
            st.write(f"*{row['autor']} · {row['curso_det']} · {row['ano_defesa']}*")
            st.write(row["resumo"] if str(row["resumo"]).strip() else
                     "_(sem resumo na fonte)_")

# Aba 7 — Cobertura de Coleta
if secao == SECOES[6]:
    st.subheader("Cobertura de Coleta: TCCs × Egressos")

    # carregar dados de egressos
    try:
        egressos = pd.read_csv(BASE / "dados" / "egressos_por_curso.csv")
        egressos_serie = pd.read_csv(BASE / "dados" / "egressos_serie_historica.csv")

        # MAPEAMENTO: curso_fonte (TCCs) → curso (egressos) — OPÇÃO A
        mapeamento_curso_fonte = {
            "História": "História (L)",
            "Insikiran – Ciências Sociais": "Insikiran — Ciências Sociais",
            "Insikiran – Ciências da Natureza": "Insikiran — Ciências da Natureza",
            "Insikiran – Comunicação e Artes": "Insikiran — Comunicação e Artes",
            "LEDUCAR – Ciências Humanas e Sociais": "LEDUCAR — Ciências Humanas e Sociais",
            "Pedagogia": "Pedagogia",
            "Música": "Música",
            "Matemática": "Matemática (L)",
            "Letras – Inglês": "Letras — Inglês (nova estrutura)",
            "Letras – Português": "Letras — Português (nova estrutura)",
            "Letras – Curso anterior": "Letras — Hab. Literatura/Português (antiga)",
        }

        # Contar TCCs por curso_fonte (desagregado)
        tccs_por_fonte = df.groupby("curso_fonte").size().reset_index(name="tccs_coletados")
        # Mapear curso_fonte para curso (egressos)
        tccs_por_fonte["curso"] = tccs_por_fonte["curso_fonte"].map(mapeamento_curso_fonte)
        # Agrupar por curso mapeado para consolidar
        tccs_map = tccs_por_fonte.groupby("curso")["tccs_coletados"].sum().to_dict()

        # Usar egressos como base (mantém todas as habilitações/variações)
        cobertura = egressos.copy()

        # Adicionar coluna de TCCs usando o mapa (mostra 0 para cursos sem TCCs)
        cobertura["tccs_coletados"] = cobertura["curso"].map(tccs_map).fillna(0).astype(int)

        # Calcular cobertura
        cobertura["cobertura_pct"] = (cobertura["tccs_coletados"] / cobertura["egressos_total"] * 100)

        # Ordenar por cobertura
        cobertura = cobertura.sort_values("cobertura_pct", ascending=False)

        # exibir tabela (linha própria)
        st.markdown("#### Cobertura por Curso")
        # formatador customizado para vírgula (2 casas decimais)
        cobertura_display = cobertura[["curso", "tccs_coletados", "egressos_total", "cobertura_pct"]].copy()
        cobertura_display["Cobertura %"] = cobertura_display["cobertura_pct"].apply(
            lambda x: f"{x:.2f}".replace(".", ",") + "%"
        )
        st.dataframe(cobertura_display[["curso", "tccs_coletados", "egressos_total", "Cobertura %"]].rename(
            columns={"curso": "Curso", "tccs_coletados": "TCCs", "egressos_total": "Egressos"}
        ), use_container_width=True, hide_index=True)

        # gráfico de cobertura (linha própria)
        st.markdown("#### Cobertura por Curso (gráfico)")
        cob_graf = cobertura.sort_values("cobertura_pct").copy()
        cob_graf["cobertura_txt"] = cob_graf["cobertura_pct"].apply(
            lambda x: f"{x:.2f}".replace(".", ",") + "%")
        fig = px.bar(cob_graf,
                    x="cobertura_pct", y="curso",
                    text="cobertura_txt",
                    color_discrete_sequence=[PALETA[0]],
                    labels={"cobertura_pct": "Cobertura (%)", "curso": "Curso"})
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=max(400, len(cob_graf) * 26),
                          xaxis_title="Cobertura (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        # gráfico temporal
        st.markdown("#### Cobertura Temporal (Série Histórica)")

        # Mapa de curso_fonte para contar TCCs por período
        tccs_por_curso_fonte = df.groupby("curso_fonte").size().to_dict()

        # calcular cobertura por período — DESAGREGADO POR CURSO
        coberturas_periodo = []
        for periodo in egressos_serie["periodo"].unique():
            periodo_data = egressos_serie[egressos_serie["periodo"] == periodo]
            for _, row in periodo_data.iterrows():
                curso = row["curso"]
                egressos_acum = row["egressos_acumulado"]

                # Encontrar curso_fonte que mapeia para este curso
                curso_fonte_match = None
                for cf, c_mapeado in mapeamento_curso_fonte.items():
                    if c_mapeado == curso:
                        curso_fonte_match = cf
                        break

                tccs = tccs_por_curso_fonte.get(curso_fonte_match, 0) if curso_fonte_match else 0
                cobertura_pct = (tccs / egressos_acum * 100) if egressos_acum > 0 else 0
                coberturas_periodo.append({
                    "periodo": periodo,
                    "curso": curso,
                    "tccs": tccs,
                    "egressos": egressos_acum,
                    "cobertura": cobertura_pct
                })

        if coberturas_periodo:
            cob_df = pd.DataFrame(coberturas_periodo)
            # agrupar por período e curso para evitar duplicação
            cob_agg = cob_df.groupby(["periodo", "curso"]).first().reset_index()
            cob_agg["cobertura_txt"] = cob_agg["cobertura"].apply(
                lambda x: f"{x:.2f}".replace(".", ",") + "%")
            fig2 = px.bar(cob_agg, x="periodo", y="cobertura", color="curso",
                         text="cobertura_txt", barmode="group",
                         color_discrete_sequence=PALETA,
                         labels={"cobertura": "Cobertura (%)", "periodo": "Período", "curso": "Curso"})
            fig2.update_traces(textposition="outside")
            fig2.update_layout(height=450, hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

        st.info("""
        **Nota sobre interpretação:**
        - Cobertura = TCCs coletados ÷ egressos do período
        - A janela 2015–2025 é padrão pois o acervo digitalizado concentra defesas recentes
        - Dados exploratórios — não censitários — ver relatório metodológico LIDAE
        """)

        st.markdown("---")
        st.markdown("#### 📋 Lista de TCCs coletados (por curso)")
        cursos_cob = ["(todos)"] + ORDEM_CURSOS
        sel_c = st.selectbox("Filtrar por curso", cursos_cob, key="cob_filtro")
        flt = df if sel_c == "(todos)" else df[df["grupo_tcc"] == sel_c]
        lista_tccs(flt, key="cob",
                   cols=["id", "curso_det", "titulo", "autor", "ano_num", "pag_num"])

        st.markdown("---")
        st.subheader("TCCs catalogados por pesquisador")
        st.caption("Esforço de catalogação por pessoa (todo o corpus).")
        vp = df[df["pesquisador"].notna() & (df["pesquisador"] != "")][
            "pesquisador"].value_counts().reset_index()
        vp.columns = ["pesquisador", "n"]
        if not vp.empty:
            fig = px.bar(vp, x="n", y="pesquisador", orientation="h", text="n",
                         color_discrete_sequence=[PALETA[2]])
            fig.update_layout(showlegend=False, height=max(250, len(vp) * 30),
                              yaxis={"categoryorder": "total ascending"},
                              xaxis_title="TCCs catalogados", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Nenhum pesquisador registrado.")

    except Exception as e:
        st.error(f"Erro ao carregar dados de egressos: {e}")

st.markdown("---")
st.caption("Fonte: 2 formulários de catalogação (Google Forms), consolidados em "
           "145 TCCs únicos (2 duplicatas removidas) + série histórica de egressos "
           "LIDAE. Dados exploratórios — ver relatório metodológico LIDAE.")

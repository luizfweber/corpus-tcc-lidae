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
import networkx as nx
from collections import Counter

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
# HABILITAÇÕES — cursos AGREGADOS em grupo_tcc (Insikiran, LEDUCARR, Letras) têm
# sub-habilitação distinta (CLAUDE.md §5). Mapeia curso_fonte → rótulo;
# os demais cursos permanecem pelo grupo_tcc.
# ─────────────────────────────────────────────────────────────────────────────
SPLIT_HABILITACAO = {
    "Insikiran – Ciências da Natureza": "Insikiran — Ciências da Natureza",
    "Insikiran – Ciências Sociais":     "Insikiran — Ciências Sociais",
    "Insikiran – Comunicação e Artes":  "Insikiran — Comunicação e Artes",
    "LEDUCARR – Ciências Humanas e Sociais":        "LEDUCARR — Ciências Humanas e Sociais",
    "LEDUCARR – Ciências da Natureza e Matemática": "LEDUCARR — Ciências da Natureza e Matemática",
    "Letras – Inglês":                  "Letras — Inglês (nova estrutura)",
    "Letras – Português":               "Letras — Português (nova estrutura)",
    "Letras – Curso anterior":          "Letras — Hab. Literatura/Português (antiga)",
}

def curso_habilitacao(row):
    """Rótulo de curso desagregado por habilitação (Insikiran, LEDUCARR e Letras)."""
    if row["grupo_tcc"] in ("Insikiran", "LEDUCARR", "Letras"):
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
    # PRESERVA acentos na exibição (CLAUDE.md §6 — a grafia é mantida).
    # A remoção de diacríticos ocorre apenas em norm_nome_agressiva (fuzzy matching).
    # remove TODOS os pontos (incluindo iniciais de nomes: J.C. → JC)
    s = s.replace(".", " ")
    # remove pontuação exceto espaço e apóstrofo (preserva d'Acampora, d'Ávila)
    s = re.sub(r"[^\w\s'’]", " ", s)
    # colapsa espaços
    s = re.sub(r"\s+", " ", s).strip()
    # Title Case com conectivos em minúscula (de, da, dos…) e apóstrofo correto
    s = " ".join(_title_palavra(w, i == 0) for i, w in enumerate(s.split()) if w)
    return s

# conectivos de nomes próprios em português — minúsculos (exceto se 1ª palavra)
_CONECTIVOS_NOME = {"de", "da", "do", "das", "dos", "e"}

def _title_palavra(w, primeira):
    """Capitaliza uma palavra de nome; conectivos em minúscula; trata d'Acampora."""
    wl = w.lower()
    if not primeira and wl in _CONECTIVOS_NOME:
        return wl
    for ap in ("'", "’"):
        if ap in w:
            a, b = w.split(ap, 1)
            return a.lower() + ap + (b[:1].upper() + b[1:].lower() if b else "")
    return w[:1].upper() + w[1:].lower()

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
# Atualizado com K=8 (211 TCCs, re-treino 2026-06-20 com palavras-chave separadas
# e limpas; K fixado por leitura) — rótulos PROVISÓRIOS.
TOPICOS = {
    0: {"rotulo": "História, gênero e mulheres (provisório)",
        "leitura": "história social/política de Roraima, gênero, representação das mulheres",
        "termos": "historia, mulheres, roraima, representacao, social, genero, "
                  "sociais, operacoes, analise, politica"},
    1: {"rotulo": "Matemática — Teoria Histórico-Cultural (provisório)",
        "leitura": "atividade de situações-problema, etapas de Galperin, resolução",
        "termos": "atividade, problema, situacoes, teoria, resolucao, acoes, "
                  "estudantes, discente, matematica, galperin"},
    2: {"rotulo": "Boa Vista, região amazônica e jogos (provisório)",
        "leitura": "contexto roraimense/amazônico, jogos e música — tópico difuso",
        "termos": "vista, regiao, roraima, jogos, processo, estado, tambem, "
                  "musica, amazonia, analise"},
    3: {"rotulo": "Prática pedagógica, artesanato e migração (provisório)",
        "leitura": "coordenação pedagógica, artesanato indígena, migrantes — tópico pequeno",
        "termos": "pedagogica, coordenacao, indigenas, artesanato, vista, analise, "
                  "roraima, artesanatos, migrantes, desafios"},
    4: {"rotulo": "Plantas medicinais e saberes tradicionais (provisório)",
        "leitura": "etnobotânica, plantas/remédios medicinais, química, conhecimento tradicional",
        "termos": "comunidade, plantas, medicinais, indigena, moradores, quimica, "
                  "culturais, tradicional, vista, remedios"},
    5: {"rotulo": "Formação docente e residência pedagógica (provisório)",
        "leitura": "formação de professores, programas (PIBID/residência), prática docente",
        "termos": "formacao, educacao, docente, contexto, pedagogica, programa, "
                  "praticas, pratica, processo, residencia"},
    6: {"rotulo": "Pedagogia, estágio e educação musical (provisório)",
        "leitura": "estágio supervisionado, experiência na pedagogia e na música",
        "termos": "educacao, estagio, roraima, pedagogia, formacao, experiencia, "
                  "vista, musical, projeto, musica"},
    7: {"rotulo": "Educação escolar indígena (provisório)",
        "leitura": "comunidade, escola e língua indígena (96% com menção indígena)",
        "termos": "indigena, comunidade, indigenas, estadual, educacao, escolar, "
                  "lingua, proposta, matematica, conhecimentos"},
}

# ─────────────────────────────────────────────────────────────────────────────
# GAZETTEER REGIONAL (povos e territórios indígenas de Roraima) + utilitários
# de texto/rede usados pelos relatórios novos. Variantes ortográficas agrupadas
# sob um nome canônico (exibição). Detecção = MENÇÃO, não centralidade.
# ─────────────────────────────────────────────────────────────────────────────
GZ_POVOS = {
    "Macuxi": ["macuxi", "makuxi"],
    "Wapichana": ["wapichana", "wapixana"],
    "Taurepang": ["taurepang", "taulipang"],
    "Ingarikó": ["ingariko", "ingarico"],
    "Patamona": ["patamona"],
    "Yanomami": ["yanomami", "yanomame", "yanomam"],
    "Ye'kwana": ["yekwana", "ye'kwana", "yekuana", "maiongong"],
    "Wai-Wai": ["waiwai", "wai-wai", "wai wai"],
    "Sapará": ["sapara", "zapara"],
    "Pirititi": ["pirititi"],
    "Waimiri-Atroari": ["waimiri", "atroari"],
    "Warao": ["warao"],
}
GZ_TERRITORIOS = {
    "Raposa Serra do Sol": ["raposa serra do sol", "raposa-serra do sol",
                            "comunidade raposa"],
    "São Marcos": ["sao marcos"],
    "Terra Indígena Yanomami": ["terra indigena yanomami"],
    "Malacacheta": ["malacacheta"],
    "Tabalascada": ["tabalascada"],
    "Serra da Moça": ["serra da moca"],
    "Waimiri-Atroari (TI)": ["waimiri-atroari"],
    "Ananás": ["ananas"],
    "Manoa-Pium": ["manoa-pium"],
    "Ponta da Serra": ["ponta da serra"],
    "Boqueirão": ["boqueirao"],
}

def _fold_gz(s):
    """minúsculas, sem acento, só [a-z0-9'- ] — para casar termos do gazetteer."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9'\- ]", " ", s)).strip()

def _pat_gz(variantes):
    alt = "|".join(re.escape(_fold_gz(v)) for v in variantes)
    return r"(?<![a-z0-9])(?:" + alt + r")(?![a-z0-9])"

def conta_gazetteer(txt_serie, grupos):
    rows = []
    for nome, variantes in grupos.items():
        n = int(txt_serie.str.contains(_pat_gz(variantes), regex=True).sum())
        if n:
            rows.append({"nome": nome, "n": n})
    return (pd.DataFrame(rows).sort_values("n", ascending=False)
            if rows else pd.DataFrame(columns=["nome", "n"]))

def _tem_valor(x):
    s = str(x).strip().lower()
    return s not in ("", "nan", "não informado", "nao informado", "não se aplica",
                     "nao se aplica", "não", "-", "—", "none")

_STOP_KW = {"de", "da", "do", "e", "a", "o", "em", "na", "no", "para", "com",
            "dos", "das", "as", "os"}

def parse_keywords(s):
    """Divide o campo palavras-chave em (grafia_original, chave_normalizada)."""
    out = []
    for p in re.split(r"[.;,\n/]| - ", str(s)):
        original = p.strip(" .;,-")
        if len(original) < 3:
            continue
        chave = unicodedata.normalize("NFKD", original.lower())
        chave = "".join(c for c in chave if not unicodedata.combining(c)).strip()
        if not chave or chave in _STOP_KW:
            continue
        out.append((original, chave))
    return out

_NAO_KW = re.compile(r'^\s*n[ãa]o\s*(info|se aplica)', re.I)

def split_palavras_chave(val):
    """Separa as palavras-chave preservando a grafia, detectando o separador por
    entrada (; , quebra de linha ou ponto). Espelha o relatorio_palavras_chave.xlsx."""
    if not _tem_valor(val):
        return []
    s = str(val).strip()
    if _NAO_KW.match(s):
        return []
    s = re.sub(r'^\s*palavras?[\s-]*chave[\s]*[:\-–]?\s*', '', s, flags=re.I)
    if ";" in s:
        partes = re.split(r"[;\n]", s)
    elif "\n" in s:
        partes = s.split("\n")
    elif "," in s:
        partes = s.split(",")
    else:
        partes = s.split(".")
    return [t for t in (p.strip().strip(".;,").strip() for p in partes) if t]

_INST_KW = ("universidade", "federal", "instituto", "faculdade", "campus",
            "departamento", "ufrr", "uerr", "ifrr", "secretaria", "colegiado")

_TITULO_BANCA = re.compile(
    r'^[\s,;\.ª°]*(?:Professor[a]?\s*(?:Dr\.?a?\.?\s*|Me\.?\s*|M\.?Sc\.?\s*)?'
    r'|Prof\.?[ao]?\.?\s*(?:Dr\.?a?\.?\s*|Me\.?\s*|M\.?Sc\.?\s*|MSc\.?\s*|Mcs\.?\s*|Mc\.?\s*)?'
    r'|Dr\.?[ao]?\.?\s*|Me\.?\s*|M\.?Sc\.?\s*|MSc\.?\s*|Mcs\.?\s*|Mc\.?\s*'
    r'|Esp(?:ecialista)?\.?\s*|Mestre\s*|Doutor[a]?\s*)+',
    re.IGNORECASE
)
_NAO_INFO = re.compile(r'^n[ãa]o\s*inform', re.IGNORECASE)

def parse_banca(val):
    """Extrai nomes de examinadores do campo de banca (texto livre)."""
    if not _tem_valor(val):
        return []
    seen, out = set(), []
    for p in re.split(r"[;\n|]|,| e ", str(val)):
        p = p.strip()
        if not p or _NAO_INFO.match(p):
            continue
        nm = _TITULO_BANCA.sub('', p).strip()
        nm = limpa_nome(nm)
        if not nm:
            continue
        low = _fold_gz(nm)
        if any(w in low for w in _INST_KW):
            continue
        if len(nm.split()) >= 2 and len(nm) > 5 and nm not in seen:
            seen.add(nm)
            out.append(nm)
    return out

def fig_rede(G, cor_no=PALETA[1]):
    """Grafo de rede em Plotly (layout spring). Nós dimensionados por 'size'."""
    if G.number_of_nodes() == 0:
        return None
    pos = nx.spring_layout(G, seed=42, k=0.7)
    ex, ey = [], []
    for a, b in G.edges():
        x0, y0 = pos[a]; x1, y1 = pos[b]
        ex += [x0, x1, None]; ey += [y0, y1, None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
                             line=dict(width=0.6, color="#C2C7BE"), hoverinfo="none"))
    xs, ys, sizes, hov = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]; xs.append(x); ys.append(y)
        s = G.nodes[n].get("size", 1); sizes.append(s)
        hov.append(f"{n} ({s})")
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text", text=list(G.nodes()),
        textposition="top center", textfont=dict(size=10),
        marker=dict(size=[9 + 3 * s for s in sizes], color=cor_no,
                    line=dict(width=1, color="white")),
        hovertext=hov, hoverinfo="text"))
    fig.update_layout(showlegend=False, height=520,
                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                      margin=dict(l=10, r=10, t=10, b=10))
    return fig

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
def carregar(_mtime: float = 0.0):
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


df = carregar(_mtime=CSV.stat().st_mtime)
N_TOTAL = len(df)

# curso desagregado por habilitação (Insikiran, LEDUCARR e Letras); usado em filtros e gráficos
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
    "tem_indigena": "Menção indígena", "situacao_banca": "Situação banca",
    "n_membros_banca": "Nº membros",
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


def lista_faltando(dados, col, rotulo, key):
    """Expander com os TCCs sem o campo `col` no cadastro do NECPF.
    Ausência = lacuna de coleta, não inexistência (CLAUDE.md §2 — não imputar)."""
    if col in ("ano_num", "pag_num"):
        falta = dados[dados[col].isna()]
    else:
        falta = dados[~dados[col].apply(_tem_valor)]
    n = len(falta)
    with st.expander(f"🔎 TCCs sem {rotulo} cadastrado — {n}", expanded=False):
        if n == 0:
            st.success(f"Todos os TCCs do filtro têm {rotulo} cadastrado.")
            return
        st.caption("Lacuna no cadastro do NECPF — não inexistência. "
                   "Excluídos das estatísticas do campo (CLAUDE.md §2).")
        cols = [c for c in ["id", "curso_det", "titulo", "autor", "ano_num",
                            "orientador"] if c in falta.columns]
        d = falta[cols].copy()
        if "ano_num" in d.columns:
            d["ano_num"] = d["ano_num"].apply(lambda x: "" if pd.isna(x) else str(int(x)))
        st.dataframe(d.rename(columns=ROTULOS_COLS),
                     use_container_width=True, hide_index=True)


# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("📚 Corpus de TCCs — Licenciaturas UFRR")
st.caption("Laboratório de Indicadores, Dados e Analítica Educacional · LIDAE/NECPF · "
           "Piloto exploratório")
st.info("**Análise exploratória, não censitária.** Cada número é indício a "
        "interpretar, não conclusão. Corpus-piloto desbalanceado — grupos com "
        "poucos TCCs (LEDUCARR, Letras) têm estatísticas instáveis.")

# ── Navegação (menu lateral com ícones) ──
SECOES = ["Distribuição", "Tópicos (LDA)", "Por curso", "Menção indígena",
          "Orientadores", "Explorar TCCs", "Cobertura de Coleta",
          "Povos & territórios", "Palavras-chave", "Bancas", "Orientador × tema"]
with st.sidebar:
    secao = option_menu(
        "Navegação", SECOES,
        icons=["bar-chart-line", "diagram-3", "mortarboard", "feather",
               "people", "search", "graph-up-arrow",
               "geo-alt", "tags", "people-fill", "grid-3x3-gap"],
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
so_com_banca = st.sidebar.checkbox("Apenas com banca cadastrada",
                                   help="Mostra só TCCs cuja banca examinadora "
                                        "foi registrada no cadastro do NECPF (exclui "
                                        "vazios e 'não informado').")
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
if so_com_banca:
    f = f[f["banca_examinadora"].apply(_tem_valor)]

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
          help="Campo do cadastro do NECPF; ausência = lacuna de coleta, "
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
    st.caption("Insikiran, LEDUCARR e Letras aparecem desagregados por habilitação; "
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

    st.subheader("Egressos × TCCs cadastrados — por curso (ano a ano)")
    st.caption("Selecione um curso. Para cada ANO: egressos formados (fonte PROEG, "
               "tabela de graduados Paricarana) e quantos TCCs desse curso já foram "
               "cadastrados (por ano de defesa), com a cobertura %. Independe dos "
               "filtros da barra lateral.")

    _ano = pd.read_csv(BASE / "dados" / "egressos_por_ano.csv")
    # exclui habilitações não informadas (egressos sem habilitação atribuível —
    # não entram na cobertura por habilitação; CLAUDE.md §2: não imputar)
    _cursos = sorted(c for c in _ano["curso_det"].dropna().unique()
                     if "habilitação não informada" not in str(c).lower())
    sel_curso = st.selectbox("Curso (com habilitação)", _cursos, key="cob_curso_ano")

    # casa a nomenclatura dos TCCs (curso_fonte) com a dos egressos PROEG (curso_det)
    TCC2DET = {
        "Insikiran – Ciências da Natureza": "Insikiran — Ciências da Natureza",
        "Insikiran – Ciências Sociais": "Insikiran — Ciências Sociais",
        "Insikiran – Comunicação e Artes": "Insikiran — Comunicação e Artes",
        "Letras – Inglês": "Letras — Português/Inglês",
        "Letras – Português": "Letras — Português",
        "Letras – Curso anterior": "Letras — Antiga estrutura curricular",
        "LEDUCARR – Ciências Humanas e Sociais": "LEDUCARR — Ciências Humanas e Sociais",
        "LEDUCARR – Ciências da Natureza e Matemática": "LEDUCARR — Ciências da Natureza e Matemática",
    }
    _dft = df.copy()
    _dft["_det"] = _dft.apply(
        lambda r: TCC2DET.get(r["curso_fonte"], r["grupo_tcc"]), axis=1)

    egr = (_ano[_ano["curso_det"] == sel_curso].groupby("ano")["egressos"]
           .sum().astype(int))
    tcc = (_dft[_dft["_det"] == sel_curso].dropna(subset=["ano_num"])
           .assign(_a=lambda d: d["ano_num"].astype(int)).groupby("_a").size())

    anos_todos = sorted(set(egr.index) | set(tcc.index))
    if not anos_todos:
        st.info("Sem dados para este curso.")
    else:
        amin, amax = int(min(anos_todos)), int(max(anos_todos))
        d0 = min(max(amin, 2015), amax)
        faixa = st.slider("Faixa de anos", amin, amax, (d0, amax), key="cob_anos")
        anos = list(range(faixa[0], faixa[1] + 1))
        cob = pd.DataFrame({"ano": anos})
        cob["egressos"] = cob["ano"].map(egr).fillna(0).astype(int)
        cob["tccs"] = cob["ano"].map(tcc).fillna(0).astype(int)
        cob["cob"] = (cob["tccs"] / cob["egressos"] * 100).where(cob["egressos"] > 0, 0)

        fig = go.Figure()
        fig.add_bar(x=cob["ano"], y=cob["egressos"], name="Egressos",
                    marker_color=PALETA[1], text=cob["egressos"])
        fig.add_bar(x=cob["ano"], y=cob["tccs"], name="TCCs cadastrados",
                    marker_color=PALETA[0], text=cob["tccs"])
        fig.update_layout(barmode="group", height=440, xaxis_title="Ano",
                          yaxis_title="Quantidade", legend_title="")
        fig.update_xaxes(tickmode="linear", dtick=1, tickangle=-45, tickformat="d")
        st.plotly_chart(fig, use_container_width=True)

        cob["Cobertura"] = cob["cob"].apply(lambda x: f"{x:.1f}".replace(".", ",") + "%")
        cob_disp = cob[["ano", "egressos", "tccs", "Cobertura"]].copy()
        cob_disp["ano"] = cob_disp["ano"].astype(str)   # ano como texto: "2015", sem separador
        st.dataframe(cob_disp.rename(
            columns={"ano": "Ano", "egressos": "Egressos", "tccs": "TCCs cadastrados"}),
            use_container_width=True, hide_index=True)
        tot_e, tot_t = int(cob["egressos"].sum()), int(cob["tccs"].sum())
        cobg = (tot_t / tot_e * 100) if tot_e else 0
        st.caption(f"Curso: **{sel_curso}**. Em {faixa[0]}–{faixa[1]}: {tot_t} TCCs "
                   f"cadastrados / {tot_e} egressos = "
                   + f"{cobg:.1f}".replace('.', ',') + "% de cobertura. "
                   "Egressos: fonte PROEG (anual). Cobertura = TCCs ÷ egressos.")

    st.subheader("Páginas por curso (mediana)")
    st.caption("Agrupado por curso/habilitação — fonte: coluna `curso_fonte` "
               "(Insikiran, LEDUCARR e Letras desagregados). Mediana, não média (CLAUDE.md §7).")
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

    st.markdown("---")
    lista_faltando(f, "ano_num", "ano de defesa", "falta_ano")
    lista_faltando(f, "pag_num", "nº de páginas", "falta_pag")

# Aba 2 — Tópicos LDA
if secao == SECOES[1]:
    st.subheader("Distribuição de tópicos (modelagem LDA, K=8)")
    st.caption("⚠️ Rótulos APROXIMADOS, derivados dos termos mais prováveis. "
               "Tópico ≠ categoria sociológica; requer revisão qualitativa.")
    fdt = f.dropna(subset=["topico_dom"]).copy()
    fdt["topico_rotulo"] = fdt["topico_dom"].map(
        lambda i: TOPICOS.get(int(i), {}).get("rotulo", f"Tópico {int(i)}"))

    st.markdown("**Proporção de TCCs por tópico dominante**")
    vt = fdt["topico_rotulo"].value_counts().reset_index()
    vt.columns = ["topico", "n"]
    fig = px.pie(vt, names="topico", values="n", hole=0.45,
                 color_discrete_sequence=PALETA)
    fig.update_layout(height=420, legend_title="Tópico dominante")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Tópico dominante × grupo de curso**")
    ct = pd.crosstab(fdt["topico_rotulo"], fdt["grupo_tcc"])
    ct = ct[[c for c in ORDEM_CURSOS if c in ct.columns]]  # ordem canônica
    fig = px.imshow(ct, text_auto=True, color_continuous_scale=SEQ_NECPF,
                    aspect="auto")
    fig.update_layout(height=460, xaxis_title="", yaxis_title="")
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
    st.subheader("📖 Como descobrimos os 'assuntos' dos TCCs: a técnica LDA")
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
    st.subheader("Presença de menção indígena por curso (com habilitações)")
    st.caption("CRITÉRIO: lista de 26 termos (indígena, intercultural, macuxi, "
               "wapichana, wai wai, terra indígena…) buscada em título + resumo "
               "+ palavras-chave. Capta MENÇÃO, não centralidade. Sujeito a "
               "falsos positivos/negativos.")

    with st.expander("📖 Como identificamos a cultura indígena nos TCCs (metodologia)"):
        st.markdown("""
*Uma explicação para quem não é da área de dados.*

#### O problema que queríamos resolver
Reunimos os trabalhos de conclusão de curso (TCCs) das licenciaturas da UFRR e
queríamos responder a uma pergunta aparentemente simples:

> Quais desses trabalhos falam sobre cultura indígena — e quão central é esse tema em cada um?

Ler todos os trabalhos inteiros, um por um, levaria muito tempo. Por isso, buscamos
uma forma de o computador nos ajudar a **encontrar e organizar** esses trabalhos. Mas,
como veremos, o computador ajuda a procurar — quem decide é sempre uma pessoa.

#### A primeira ideia (e por que ela não basta)
A solução óbvia seria: *peça ao computador para procurar a palavra "indígena"*. Onde
ela aparecer, marque o trabalho. Isso funciona em parte, mas tem dois furos:

1. **Palavras que parecem indicar o tema, mas nem sempre indicam.** Palavras como
   *"povos"* ou *"tradicional"* aparecem em muitos contextos. "Família tradicional",
   "métodos tradicionais de ensino", "os povos da Antiguidade" — nada disso é sobre
   cultura indígena.
2. **Trabalhos que falam do tema sem usar a palavra exata.** Um TCC pode tratar
   profundamente da cultura Macuxi sem nunca escrever a palavra "indígena".

Ou seja: a busca simples **erra para os dois lados** — marca trabalhos que não deveria
e perde trabalhos que deveria encontrar.

#### A ideia melhor: um "dicionário regional" (gazetteer)
Pense num detetive tentando descobrir de qual cidade veio uma carta anônima. Ele não
procura uma única palavra — procura **pistas locais**: o nome de uma rua, de um time
pequeno, de uma comida típica. Foi isso que montamos: uma lista curada de **pistas da
cultura indígena de Roraima** (no jargão técnico, um **gazetteer**). A nossa reúne:

- **Nomes de povos** — Macuxi, Wapichana, Yanomami, Taurepang, Ye'kwana e outros.
- **Nomes de lugares** — terras indígenas como Raposa Serra do Sol e São Marcos; "maloca".
- **Línguas e famílias linguísticas** — Karib, Aruak, "língua macuxi".
- **Instituições e temas da educação indígena** — Insikiran, escola indígena, magistério indígena.

A grande vantagem: muitas dessas pistas são **inconfundíveis**. Ninguém escreve
"Yanomami" ou "Macuxi" por acaso — diferente de "tradicional", que pode aparecer em
qualquer assunto.

#### A sacada principal: nem toda pista vale o mesmo
Em vez de tratar todas as palavras como prova igual, nós as separamos por **nível de
confiança**, como faria um detetive ao pesar evidências:

| Nível de confiança | Exemplos | O que significa |
|---|---|---|
| **Pista forte** | Macuxi, Yanomami, Raposa Serra do Sol, Insikiran | Praticamente garante que o tema está presente. |
| **Pista média** | interculturalidade, etnomatemática, tuxaua, pajé | Sugere o tema, mas vale conferir. |
| **Pista fraca (ambígua)** | povos, tradicional, etnia | **Não conta sozinha.** Só vira indício com uma pista mais forte. |

Um trabalho que menciona "Macuxi" é classificado com segurança. Já um que só diz
"povos tradicionais" fica marcado como **"precisa de revisão humana"**.

#### O computador procura, mas o ser humano decide
O computador faz a parte cansativa: varre os trabalhos em segundos e separa três grupos
— os de **pistas fortes** (alta confiança), os de só **pistas fracas** (zona cinzenta,
para revisar) e os **sem pista alguma**. Mas a palavra final é sempre de uma pessoa, que
lê os casos de fronteira. A máquina **estreita o trabalho**; não substitui o julgamento.

#### O que descobrimos ao testar
Tínhamos colocado a palavra *"indígena"* como **pista fraca**, por achá-la ambígua. Mas,
ao revisar, percebemos que **neste conjunto específico** — TCCs de licenciatura de
Roraima, boa parte do curso intercultural Insikiran — a palavra "indígena" quase sempre
indica mesmo o tema. A lição: **a régua precisa ser ajustada ao material analisado.**

Também notamos que faltavam na lista os **nomes das comunidades indígenas** (como
Maturuca e Anta II). Incluí-los é o próximo passo — e gera um benefício extra: uma lista
organizada de comunidades de Roraima, útil para futuras pesquisas do laboratório.

> 💡 As **pistas fortes** (povos e territórios) estão mapeadas na aba **"Povos & territórios"**.

#### Um aviso importante
Encontrar a palavra **não é o mesmo** que provar que o trabalho gira em torno do tema.
Um TCC pode citar "Macuxi" de passagem; outro pode ser inteiramente dedicado à cultura
Macuxi. Por isso, tudo o que esse método produz são **indícios exploratórios** — um mapa
para guiar a leitura, não uma conclusão pronta.

---
*Documento produzido no âmbito do LIDAE — Laboratório de Indicadores, Dados e Analítica
Educacional (NECPF/UFRR).*
""")

    g = f.groupby("curso_det")["tem_indigena"].agg(["sum", "count"]).reset_index()
    g["_o"] = pd.Categorical(g["curso_det"], categories=ORDEM_CURSOS_DET, ordered=True)
    g = g.sort_values("_o").drop(columns="_o")
    g["com"] = g["sum"].astype(int)
    g["sem"] = g["count"] - g["com"]
    g["pct"] = (g["com"] / g["count"] * 100).round(0)
    fig = go.Figure()
    fig.add_bar(y=g["curso_det"], x=g["com"], orientation="h",
                name="Com menção", marker_color=PALETA[4])
    fig.add_bar(y=g["curso_det"], x=g["sem"], orientation="h",
                name="Sem menção", marker_color=CINZA_NEUTRO)
    fig.update_layout(barmode="stack", height=420, xaxis_title="Nº de TCCs",
                      yaxis_title="", legend_title="",
                      yaxis={"categoryorder": "array",
                             "categoryarray": ORDEM_CURSOS_DET[::-1]})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        g[["curso_det", "com", "count", "pct"]].rename(
            columns={"curso_det": "Curso", "com": "Com menção",
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

    st.markdown("---")
    lista_faltando(f, "orientador", "orientador", "falta_orient")

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
                     "_(sem resumo no cadastro)_")

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
            "LEDUCARR – Ciências Humanas e Sociais": "LEDUCARR — Ciências Humanas e Sociais",
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

# Aba 8 — Povos & territórios indígenas (gazetteer)
if secao == SECOES[7]:
    st.subheader("Povos e territórios indígenas citados")
    st.caption("Detecção por gazetteer regional de Roraima (etnônimos, terras "
               "indígenas, topônimos), em título + resumo + palavras-chave. "
               "Variantes ortográficas agrupadas (ex.: Macuxi/Makuxi). Capta "
               "MENÇÃO, não a centralidade do tema. Exploratório.")
    txt_gz = (f["titulo"].fillna("") + " " + f["palavras_chave"].fillna("") + " "
              + f["resumo"].fillna("")).map(_fold_gz)
    cpov = conta_gazetteer(txt_gz, GZ_POVOS)
    cter = conta_gazetteer(txt_gz, GZ_TERRITORIOS)

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Povos (etnônimos) mais citados**")
        if not cpov.empty:
            fig = px.bar(cpov.sort_values("n"), x="n", y="nome", orientation="h",
                         text="n", color_discrete_sequence=[PALETA[0]])
            fig.update_layout(showlegend=False, height=max(300, len(cpov) * 34),
                              xaxis_title="Nº de TCCs que citam", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum etnônimo citado no filtro atual.")
    with cc2:
        st.markdown("**Territórios / Terras Indígenas mais citados**")
        if not cter.empty:
            fig = px.bar(cter.sort_values("n"), x="n", y="nome", orientation="h",
                         text="n", color_discrete_sequence=[PALETA[1]])
            fig.update_layout(showlegend=False, height=max(300, len(cter) * 34),
                              xaxis_title="Nº de TCCs que citam", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum território citado no filtro atual.")

    st.markdown("**Povos citados × curso**")
    linhas = []
    for nome, variantes in GZ_POVOS.items():
        mask = txt_gz.str.contains(_pat_gz(variantes), regex=True)
        if mask.any():
            sub = f[mask.values]
            for curso, n in sub["curso_det"].value_counts().items():
                linhas.append({"Povo": nome, "Curso": curso, "n": int(n)})
    if linhas:
        ct = (pd.DataFrame(linhas)
              .pivot_table(index="Povo", columns="Curso", values="n",
                           aggfunc="sum", fill_value=0))
        fig = px.imshow(ct, text_auto=True, color_continuous_scale=SEQ_NECPF,
                        aspect="auto")
        fig.update_layout(height=max(300, len(ct) * 40), xaxis_title="",
                          yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    st.caption("⚠️ Menção ≠ centralidade: um TCC pode citar um povo de passagem.")

    # Lista de TCCs filtrada por povo/território
    st.markdown("---")
    st.markdown("#### TCCs por povo ou território citado")
    opcoes_gz = {"Todos": None}
    for nome in sorted(GZ_POVOS.keys()):
        opcoes_gz[f"Povo — {nome}"] = ("pov", nome)
    for nome in sorted(GZ_TERRITORIOS.keys()):
        opcoes_gz[f"Território — {nome}"] = ("ter", nome)
    sel_gz = st.selectbox("Filtrar por povo ou território",
                          list(opcoes_gz.keys()), key="gz_sel")
    val_gz = opcoes_gz[sel_gz]
    if val_gz is None:
        filt_gz = f
    else:
        tipo_gz, nome_gz = val_gz
        variantes_gz = (GZ_POVOS if tipo_gz == "pov" else GZ_TERRITORIOS)[nome_gz]
        mask_gz = txt_gz.str.contains(_pat_gz(variantes_gz), regex=True)
        filt_gz = f[mask_gz.values]
    st.caption(f"{len(filt_gz)} TCC(s) encontrado(s).")
    lista_tccs(filt_gz, key="gz_tccs",
               cols=["id", "curso_det", "titulo", "autor", "ano_num"])

# Aba 9 — Co-ocorrência de palavras-chave
if secao == SECOES[8]:
    st.subheader("Co-ocorrência de palavras-chave")
    st.caption("Palavras-chave informadas pelos autores (não os tópicos do LDA). "
               "Agrupadas por forma normalizada (sem acento/caixa); exibe a grafia "
               "mais frequente.")
    listas = [kw for kw in f["palavras_chave"].dropna().map(parse_keywords) if kw]
    freq, grafia = Counter(), {}
    for kws in listas:
        for original, chave in {(o, c) for o, c in kws}:
            freq[chave] += 1
            grafia.setdefault(chave, Counter())[original] += 1
    if not freq:
        st.info("Sem palavras-chave no filtro atual.")
    else:
        disp = {k: grafia[k].most_common(1)[0][0] for k in freq}
        topn = st.slider("Top N palavras-chave", 10, 40, 20, key="kw_n")
        top = [k for k, _ in freq.most_common(topn)]
        dfreq = pd.DataFrame({"kw": [disp[k] for k in top],
                              "n": [freq[k] for k in top]})
        fig = px.bar(dfreq.sort_values("n"), x="n", y="kw", orientation="h",
                     text="n", color_discrete_sequence=[PALETA[2]])
        fig.update_layout(showlegend=False, height=max(320, len(dfreq) * 26),
                          xaxis_title="Nº de TCCs", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Rede de co-ocorrência** (palavras-chave que aparecem juntas)")
        min_co = st.slider("Co-ocorrências mínimas para ligar", 1, 5, 2, key="kw_co")
        topset = set(top)
        co, nodefreq = Counter(), Counter()
        for kws in listas:
            chaves = sorted({c for _, c in kws if c in topset})
            for c in chaves:
                nodefreq[c] += 1
            for i in range(len(chaves)):
                for j in range(i + 1, len(chaves)):
                    co[(chaves[i], chaves[j])] += 1
        G = nx.Graph()
        for (a, b), w in co.items():
            if w >= min_co:
                G.add_edge(a, b, weight=w)
        for n in list(G.nodes()):
            G.nodes[n]["size"] = nodefreq[n]
        G = nx.relabel_nodes(G, {n: disp[n] for n in G.nodes()})
        figr = fig_rede(G, cor_no=PALETA[2])
        if figr:
            st.plotly_chart(figr, use_container_width=True)
        else:
            st.info("Nenhuma co-ocorrência atinge o mínimo escolhido.")
    st.caption(f"⚠️ {int(f['palavras_chave'].isna().sum())} TCCs sem palavras-chave "
               "no filtro (excluídos).")

    # ── Palavras-chave separadas por TCC (cada termo em uma coluna) ──────────
    st.markdown("---")
    st.markdown("#### 📋 Palavras-chave separadas por TCC")
    st.caption("Cada palavra-chave em sua própria coluna, preservando a grafia. "
               "Separador detectado por entrada (`;`, vírgula, quebra de linha ou "
               "ponto); rótulo 'Palavras-chave:' e pontuação final removidos.")
    kw_listas = f["palavras_chave"].map(split_palavras_chave)
    maxk = int(kw_listas.map(len).max() or 0)
    if maxk == 0:
        st.info("Sem palavras-chave separáveis no filtro atual.")
    else:
        reg = []
        for (_, row), kws in zip(f.iterrows(), kw_listas):
            d = {"id": row["id"], "Curso": row["curso_det"], "Título": row["titulo"],
                 "Autor": row["autor"],
                 "Ano": "" if pd.isna(row["ano_num"]) else str(int(row["ano_num"])),
                 "Nº": len(kws)}
            for i in range(maxk):
                d[f"Palavra-chave {i+1}"] = kws[i] if i < len(kws) else ""
            reg.append(d)
        kdf = pd.DataFrame(reg)
        st.dataframe(kdf, use_container_width=True, hide_index=True, height=360)

    st.markdown("---")
    lista_faltando(f, "palavras_chave", "palavras-chave", "falta_kw")

# Aba 10 — Rede de bancas examinadoras
if secao == SECOES[9]:
    st.subheader("Rede de bancas examinadoras")
    pct = f["banca_examinadora"].map(_tem_valor).mean() * 100 if len(f) else 0
    st.caption(f"Co-participação: dois nomes se ligam quando avaliaram o mesmo TCC. "
               f"Nomes extraídos do campo de banca (texto livre) e limpos (sem "
               f"titulação/instituição). Preenchido em ~{pct:.0f}% dos TCCs no "
               "filtro; ausência = lacuna de coleta, não inexistência de banca.")

    with st.expander("📖 Como construímos a rede de bancas (metodologia)"):
        st.markdown("""
A rede mostra **quem avaliou TCCs junto com quem**. Ela é construída em quatro
passos, a partir do campo *Membros da banca examinadora* do cadastro do NECPF —
um texto livre, preenchido com grafias e formatos variados.

**1. Leitura do campo.** Cada registro de banca é um texto único (ex.:
*"Prof. Dr. Héctor José García Mendoza — UFRR; Profa. Dra. Edileusa do Socorro…"*).
Separamos os nomes nos sinais usados pelos catalogadores: ponto-e-vírgula, barra
`|`, quebra de linha, vírgula e a conjunção "e".

**2. Limpeza de cada nome.** De cada trecho removemos:
- **Titulação** — Prof./Profa., Dr./Dra., Me., Msc., Esp., Mestre, Doutor(a)…;
- **Instituição e função** — UFRR, Universidade, Instituto, Curso de…, "membro",
  "orientador", "presidente", e o que vem entre parênteses;
- "não informado" e fragmentos com menos de duas palavras.

  A **grafia com acentos é preservada** (ex.: *Héctor José García Mendoza*); a
  remoção de acento serve só internamente, para agrupar variações do mesmo nome.

**3. Montagem da rede (co-participação).** Para cada TCC, os examinadores
formam um pequeno grupo totalmente ligado entre si — cada um se conecta a todos os
outros daquela mesma banca. Quando duas pessoas avaliam **vários** TCCs juntas, a
ligação entre elas fica **mais forte** (maior peso). O **tamanho de cada nó** é o
número de bancas em que a pessoa participou; o orientador também conta como membro.

**4. Filtro de recorrência.** O controle *"Mínimo de bancas para incluir o membro"*
remove participantes esporádicos, deixando visível o núcleo recorrente.

**Limites (leitura exploratória, CLAUDE.md §1, §4).** A extração de um texto livre
é sujeita a falhas; nomes muito abreviados ou colados podem escapar. A rede
retrata **a coleta atual**, não o universo de bancas — ausência de um vínculo
significa lacuna de cadastro, não que a co-participação não existiu.
""")

    membros_por_tcc, cont = [], Counter()
    for val in f["banca_examinadora"]:
        nomes = parse_banca(val)
        if nomes:
            membros_por_tcc.append(nomes)
            for nm in nomes:
                cont[nm] += 1
    if not cont:
        st.info("Sem dados de banca utilizáveis no filtro atual.")
    else:
        top = pd.DataFrame(cont.most_common(20), columns=["membro", "n"])
        st.markdown("**Quem mais participou de bancas**")
        fig = px.bar(top.sort_values("n"), x="n", y="membro", orientation="h",
                     text="n", color_discrete_sequence=[PALETA[1]])
        fig.update_layout(showlegend=False, height=max(320, len(top) * 26),
                          xaxis_title="Nº de bancas", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Rede de co-participação**")
        min_b = st.slider("Mínimo de bancas para incluir o membro", 1, 4, 2,
                          key="bn_min")
        G = nx.Graph()
        for nomes in membros_por_tcc:
            elig = [n for n in nomes if cont[n] >= min_b]
            for n in elig:
                G.add_node(n)
            for i in range(len(elig)):
                for j in range(i + 1, len(elig)):
                    if G.has_edge(elig[i], elig[j]):
                        G[elig[i]][elig[j]]["weight"] += 1
                    else:
                        G.add_edge(elig[i], elig[j], weight=1)
        for n in list(G.nodes()):
            G.nodes[n]["size"] = cont[n]
        figr = fig_rede(G, cor_no=PALETA[1])
        if figr:
            st.plotly_chart(figr, use_container_width=True)
        else:
            st.info("Poucos membros atingem o mínimo escolhido para formar rede.")

    # ── Lacunas no cadastro de bancas (filtrável por curso) ──────────────────
    st.markdown("---")
    st.markdown("#### 🔎 TCCs com cadastro de banca a completar")
    st.caption("Lacunas no campo de banca examinadora — para preencher a partir "
               "dos PDFs. 'Ausente' = campo vazio/'não informado'; "
               "'Incompleta' = só 1 nome registrado (banca tem ≥ 2 membros + orientador).")

    def _situacao_banca(v):
        if not _tem_valor(v):
            return "Ausente"
        n = len(parse_banca(v))
        if n == 0:
            return "Ausente"
        if n == 1:
            return "Incompleta (1 membro)"
        return "OK"

    fb = f.copy()
    fb["situacao_banca"] = fb["banca_examinadora"].map(_situacao_banca)
    fb["n_membros_banca"] = fb["banca_examinadora"].map(lambda v: len(parse_banca(v)))
    faltam = fb[fb["situacao_banca"] != "OK"]

    if faltam.empty:
        st.success("Todos os TCCs do filtro atual têm banca cadastrada (≥ 2 membros).")
    else:
        # resumo por curso (quantos faltam em cada)
        resumo = (faltam.groupby("curso_det")["situacao_banca"]
                  .value_counts().unstack(fill_value=0))
        for col in ("Ausente", "Incompleta (1 membro)"):
            if col not in resumo.columns:
                resumo[col] = 0
        resumo["Total a completar"] = resumo.sum(axis=1)
        resumo = resumo.reindex([c for c in ORDEM_CURSOS_DET if c in resumo.index])
        st.markdown("**Resumo por curso**")
        st.dataframe(resumo.reset_index().rename(columns={"curso_det": "Curso"}),
                     use_container_width=True, hide_index=True)

        cursos_op = ["Todos os cursos"] + [c for c in ORDEM_CURSOS_DET
                                           if c in faltam["curso_det"].unique()]
        sel_cf = st.selectbox("Filtrar por curso", cursos_op, key="banca_falta_curso")
        flt = faltam if sel_cf == "Todos os cursos" else faltam[faltam["curso_det"] == sel_cf]
        st.caption(f"{len(flt)} TCC(s) com cadastro de banca a completar.")
        lista_tccs(flt, key="banca_falta",
                   cols=["id", "curso_det", "situacao_banca", "n_membros_banca",
                         "titulo", "autor", "orientador", "ano_num"])

# Aba 11 — Orientador × tema (tópico LDA)
if secao == SECOES[10]:
    st.subheader("Orientador × tema (tópico LDA)")
    st.caption("Distribuição dos TCCs de cada orientador recorrente (≥2 TCCs) "
               "pelos 4 tópicos do LDA. ⚠️ Tópico é indício, não categoria; o N por "
               "orientador é pequeno — leitura qualitativa.")
    fo = f[f["orientador"].apply(_tem_valor) & f["topico_dom"].notna()].copy()
    if fo.empty:
        st.info("Sem orientador/tópico utilizável no filtro atual.")
    else:
        fo["topico_dom"] = fo["topico_dom"].astype(int)
        rec = fo["orientador"].value_counts()
        rec = rec[rec >= 2].index.tolist()
        fo = fo[fo["orientador"].isin(rec)]
        if fo.empty:
            st.info("Nenhum orientador com 2+ TCCs (com tópico) no filtro atual.")
        else:
            fo["Tópico"] = fo["topico_dom"].map(lambda i: f"T{i}")
            ct = pd.crosstab(fo["orientador"], fo["Tópico"])
            ct = ct[[c for c in [f"T{i}" for i in range(4)] if c in ct.columns]]
            fig = px.imshow(ct, text_auto=True, color_continuous_scale=SEQ_NECPF,
                            aspect="auto")
            fig.update_layout(height=max(320, len(ct) * 34), xaxis_title="Tópico",
                              yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Legenda dos tópicos:**")
            for i, info in TOPICOS.items():
                st.markdown(f"- **T{i}** — {info['rotulo']}")

st.markdown("---")
st.caption("Fonte: cadastro dos TCCs realizado pelos pesquisadores do NECPF "
           "(211 TCCs únicos), com série histórica de egressos da PROEG. "
           "Dados exploratórios — ver relatório metodológico LIDAE.")

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
from fuzzywuzzy import fuzz
import re, unicodedata

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
# Atualizado com K=5 (147 TCCs)
TOPICOS = {
    0: {"rotulo": "Educação & Música",
        "leitura": "práticas pedagógicas, música, formação, coordenação",
        "termos": "educacao, musica, musical, vista, roraima, coordenacao, "
                  "contexto, pratica, pedagogica, especial"},
    1: {"rotulo": "Indígena & Comunidade",
        "leitura": "cultura, saberes tradicionais, educação escolar indígena",
        "termos": "indigena, comunidade, indigenas, educacao, cultura, estadual, "
                  "escolar, conhecimentos, proposta, saude"},
    2: {"rotulo": "Estágio & Formação",
        "leitura": "estágio supervisionado, pedagogia, plantas medicinais",
        "termos": "estagio, pedagogia, formacao, roraima, experiencia, pedagogica, "
                  "plantas, curricular, educacao, medicinais"},
    3: {"rotulo": "Leitura & Língua",
        "leitura": "alfabetização, processos de leitura e escrita, jogos pedagógicos",
        "termos": "leitura, lingua, indigena, jogos, matematica, aluno, escrita, "
                  "comunidade, praticas, processo"},
    4: {"rotulo": "Atividade & Resolução de Problemas",
        "leitura": "Teoria Histórico-Cultural, atividade, resolução de problemas",
        "termos": "atividade, problema, situacoes, teoria, resolucao, acoes, "
                  "estudantes, discente, matematica, galperin"},
}

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="TCCs Licenciaturas UFRR — LIDAE",
                   page_icon="📚", layout="wide")


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


df = carregar()
N_TOTAL = len(df)

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("📚 Corpus de TCCs — Licenciaturas UFRR")
st.caption("Laboratório de Indicadores, Dados e Analítica Educacional · LIDAE/NECPF · "
           "Piloto exploratório")
st.info("⚠️ **Análise exploratória, não censitária.** Cada número é indício a "
        "interpretar, não conclusão. Corpus-piloto desbalanceado — grupos com "
        "poucos TCCs (LEDUCAR, Letras) têm estatísticas instáveis.", icon="⚠️")

# ── Sidebar: filtros ─────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
grupos = sorted(df["grupo_tcc"].dropna().unique())
sel_grupos = st.sidebar.multiselect("Grupo de curso", grupos, default=grupos)

anos_validos = df["ano_num"].dropna()
if not anos_validos.empty:
    amin, amax = int(anos_validos.min()), int(anos_validos.max())
    sel_anos = st.sidebar.slider("Ano de defesa", amin, amax, (amin, amax))
else:
    sel_anos = None

so_indigena = st.sidebar.checkbox("Apenas com menção indígena")
incluir_sem_ano = st.sidebar.checkbox("Incluir TCCs sem ano informado",
                                      value=True)

# aplica filtros
f = df[df["grupo_tcc"].isin(sel_grupos)].copy()
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
t1, t2, t3, t4, t5, t6, t7 = st.tabs(
    ["📊 Distribuição", "🧩 Tópicos (LDA)", "🪶 Menção indígena",
     "👥 Orientadores", "🔍 Explorar TCCs", "📖 Metodologia", "📈 Cobertura de Coleta"])

# Aba 1 — Distribuição
with t1:
    cc1, cc2 = st.columns(2)
    with cc1:
        st.subheader("TCCs por grupo de curso")
        vc = f["grupo_tcc"].value_counts().reset_index()
        vc.columns = ["grupo", "n"]
        fig = px.bar(vc, x="n", y="grupo", orientation="h",
                     text="n", color="grupo",
                     color_discrete_sequence=PALETA)
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"},
                          xaxis_title="Nº de TCCs", yaxis_title="", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with cc2:
        st.subheader("TCCs por ano de defesa")
        anos = f.dropna(subset=["ano_num"])
        n_sem = f["ano_num"].isna().sum()
        if not anos.empty:
            va = anos["ano_num"].astype(int).value_counts().sort_index().reset_index()
            va.columns = ["ano", "n"]
            fig = px.bar(va, x="ano", y="n", text="n",
                         color_discrete_sequence=[PALETA[0]])
            fig.update_layout(xaxis_title="Ano", yaxis_title="Nº de TCCs",
                              height=380)
            st.plotly_chart(fig, use_container_width=True)
        st.caption(f"⚠️ {n_sem} TCCs sem ano informado — excluídos deste gráfico "
                   "(não imputados).")
        st.caption("A curva NÃO deve ser lida como 'aumento de produção docente' "
                   "— reflete disponibilidade do acervo digitalizado.")

    st.subheader("Páginas por grupo (mediana)")
    pg = f.dropna(subset=["pag_num"])
    if not pg.empty:
        fig = px.box(pg, x="grupo_tcc", y="pag_num", color="grupo_tcc",
                     color_discrete_sequence=PALETA, points="all")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Páginas",
                          height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Boxplot mostra mediana e dispersão. "
                   f"Exclui {f['pag_num'].isna().sum()} TCCs sem nº de páginas.")

    st.subheader("TCCs catalogados por pesquisador")
    vp = f[f["pesquisador"].notna() & (f["pesquisador"] != "")]["pesquisador"].value_counts().reset_index()
    vp.columns = ["pesquisador", "n"]
    if not vp.empty:
        fig = px.bar(vp, x="n", y="pesquisador", orientation="h", text="n",
                     color_discrete_sequence=[PALETA[2]])
        fig.update_layout(showlegend=False, height=max(250, len(vp)*30),
                          yaxis={"categoryorder": "total ascending"},
                          xaxis_title="TCCs catalogados", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nenhum pesquisador registrado no filtro atual.")

# Aba 2 — Tópicos LDA
with t2:
    st.subheader("Distribuição de tópicos (modelagem LDA, K=5)")
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
        fig = px.imshow(ct, text_auto=True, color_continuous_scale="YlOrRd",
                        aspect="auto")
        fig.update_layout(height=380, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Termos mais prováveis por tópico** (revisar leituras)")
    for i, info in TOPICOS.items():
        st.markdown(f"- **{info['rotulo']}** — _{info['leitura']}_  \n"
                    f"  <span style='color:gray;font-size:0.85em'>{info['termos']}</span>",
                    unsafe_allow_html=True)

# Aba 3 — Menção indígena
with t3:
    st.subheader("Presença de menção indígena por grupo")
    st.caption("CRITÉRIO: lista de 26 termos (indígena, intercultural, macuxi, "
               "wapichana, wai wai, terra indígena…) buscada em título + resumo "
               "+ palavras-chave. Capta MENÇÃO, não centralidade. Sujeito a "
               "falsos positivos/negativos.")
    g = f.groupby("grupo_tcc")["tem_indigena"].agg(["sum", "count"]).reset_index()
    g["com"] = g["sum"].astype(int)
    g["sem"] = g["count"] - g["com"]
    g["pct"] = (g["com"] / g["count"] * 100).round(0)
    fig = go.Figure()
    fig.add_bar(y=g["grupo_tcc"], x=g["com"], orientation="h",
                name="Com menção", marker_color=PALETA[4])
    fig.add_bar(y=g["grupo_tcc"], x=g["sem"], orientation="h",
                name="Sem menção", marker_color="#D9D9D9")
    fig.update_layout(barmode="stack", height=380, xaxis_title="Nº de TCCs",
                      yaxis_title="", legend_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        g[["grupo_tcc", "com", "count", "pct"]].rename(
            columns={"grupo_tcc": "Grupo", "com": "Com menção",
                     "count": "Total", "pct": "% menção"}),
        use_container_width=True, hide_index=True)

# Aba 4 — Orientadores
with t4:
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

# Aba 5 — Explorar
with t5:
    st.subheader("Explorador de TCCs")
    busca = st.text_input("Buscar em título / resumo / palavras-chave")
    cols_show = ["id", "grupo_tcc", "titulo", "autor", "orientador",
                 "pesquisador", "ano_defesa", "paginas", "palavras_chave"]
    fe = f.copy()
    if busca:
        b = busca.lower()
        mask = (fe["titulo"].str.lower().str.contains(b, na=False) |
                fe["resumo"].str.lower().str.contains(b, na=False) |
                fe["palavras_chave"].str.lower().str.contains(b, na=False))
        fe = fe[mask]
    st.caption(f"{len(fe)} TCCs.")
    st.dataframe(fe[cols_show], use_container_width=True, hide_index=True,
                 height=400)
    with st.expander("Ver resumo completo de um TCC"):
        if not fe.empty:
            tid = st.selectbox("Selecione o id", fe["id"].tolist())
            row = fe[fe["id"] == tid].iloc[0]
            st.markdown(f"**{row['titulo']}**")
            st.write(f"*{row['autor']} · {row['grupo_tcc']} · {row['ano_defesa']}*")
            st.write(row["resumo"] if str(row["resumo"]).strip() else
                     "_(sem resumo na fonte)_")

# Aba 6 — Metodologia
with t6:
    st.subheader("Como descubrimos os 'assuntos' dos TCCs: a técnica LDA")
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

    st.info("""
    **Documentação técnica completa:**
    - [EXPLICACAO_LDA.md](https://github.com/luizfweber/corpus-tcc-lidae) — Explicação pública da metodologia LDA
    - [IDENTIDADE_VISUAL_NECPF.md](https://github.com/luizfweber/corpus-tcc-lidae) — Sistema de design e cores NECPF
    - [CLAUDE.md](https://github.com/luizfweber/corpus-tcc-lidae) — Princípios metodológicos completos
    """)

# Aba 7 — Cobertura de Coleta
with t7:
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

        # exibir tabela
        st.markdown("#### Cobertura por Curso")
        col1, col2 = st.columns(2)

        with col1:
            # formatador customizado para vírgula
            cobertura_display = cobertura[["curso", "tccs_coletados", "egressos_total", "cobertura_pct"]].copy()
            cobertura_display["Cobertura %"] = cobertura_display["cobertura_pct"].apply(
                lambda x: f"{x:.1f}".replace(".", ",") + "%"
            )
            st.dataframe(cobertura_display[["curso", "tccs_coletados", "egressos_total", "Cobertura %"]].rename(
                columns={"curso": "Curso", "tccs_coletados": "TCCs", "egressos_total": "Egressos"}
            ), use_container_width=True, hide_index=True)

        with col2:
            # gráfico de cobertura
            fig = px.bar(cobertura.sort_values("cobertura_pct"),
                        x="cobertura_pct", y="curso",
                        text="cobertura_pct",
                        color_discrete_sequence=[PALETA[0]],
                        labels={"cobertura_pct": "Cobertura (%)", "curso": "Curso"})
            fig.update_layout(showlegend=False, height=400, xaxis_title="Cobertura (%)")
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
            fig2 = px.bar(cob_agg, x="periodo", y="cobertura", color="curso",
                         text="cobertura", barmode="group",
                         color_discrete_sequence=PALETA,
                         labels={"cobertura": "Cobertura (%)", "periodo": "Período", "curso": "Curso"})
            fig2.update_layout(height=400, hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

        st.info("""
        **Nota sobre interpretação:**
        - Cobertura = TCCs coletados ÷ egressos do período
        - A janela 2015–2025 é padrão pois o acervo digitalizado concentra defesas recentes
        - Dados exploratórios — não censitários — ver relatório metodológico LIDAE
        """)

    except Exception as e:
        st.error(f"Erro ao carregar dados de egressos: {e}")

st.markdown("---")
st.caption("Fonte: 2 formulários de catalogação (Google Forms), consolidados em "
           "147 TCCs + série histórica de egressos LIDAE. Dados exploratórios — ver relatório metodológico LIDAE.")

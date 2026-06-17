# Customização de Layout — Dashboard LIDAE

## 1. Mudar para Layout WIDE (tela inteira)

No início do `dashboard.py`, mude:

```python
st.set_page_config(page_title="...", layout="wide")  # ← mude "wide"
```

- **"centered"** (padrão): conteúdo centralizado, menor
- **"wide"**: aproveita toda a largura da tela

## 2. Mudar Cores (Tema)

Edite `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2C6E91"              # azul (botões, links)
backgroundColor = "#FFFFFF"            # fundo principal
secondaryBackgroundColor = "#F0F2F6"  # fundo das caixas
textColor = "#262730"                 # cor do texto
```

Exemplos de cores:
- Azul: `#2C6E91`, `#1E88E5`, `#0D47A1`
- Verde: `#2E7D32`, `#43A047`, `#66BB6A`
- Laranja: `#E07B39`, `#F57C00`, `#FF6F00`
- Roxo: `#7B1FA2`, `#8E6BBF`, `#AB47BC`

## 3. Tema Escuro

No `config.toml`, defina:

```toml
[theme]
darkMode = true
primaryColor = "#4AABDB"  # cores mais claras para tema escuro
```

Depois recarregue o Streamlit.

## 4. Mudar Layout das Colunas no Dashboard

No código `dashboard.py`, ajuste a distribuição de colunas:

```python
# Exemplo: 3 colunas iguais
c1, c2, c3 = st.columns(3)

# Ou: 2 colunas desiguais (60% e 40%)
c1, c2 = st.columns([3, 2])

# Ou: sidebar + conteúdo
with st.sidebar:
    st.write("Filtros aqui")
st.write("Conteúdo principal aqui")
```

## 5. Adicionar Logo ou Imagem no Topo

No início do `dashboard.py`:

```python
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.title("Dashboard")
```

## 6. Customização CSS Avançada

Adicione no `dashboard.py`:

```python
st.markdown("""
<style>
    /* Mudar tamanho do título */
    h1 { font-size: 3rem; color: #2C6E91; }
    
    /* Mudar cor do fundo */
    .stApp { background-color: #F5F5F5; }
    
    /* Estilo das abas */
    .stTabs [data-baseweb="tab-list"] button { color: #2C6E91; }
</style>
""", unsafe_allow_html=True)
```

## 7. Reorganizar as Abas

No código das abas:

```python
t1, t2, t3, t4, t5 = st.tabs([
    "📊 Distribuição",      # reordene aqui
    "🧩 Tópicos",
    "🪶 Indígena",
    "👥 Orientadores",
    "🔍 Explorar"
])
```

## 8. Salvar Configuração Localmente

Para guardar suas preferências:
1. Edite `.streamlit/config.toml`
2. Ou use as variáveis de ambiente:
   ```bash
   export STREAMLIT_THEME_primaryColor="#2C6E91"
   streamlit run dashboard.py
   ```

## 9. Recarregar o Dashboard

Após editar `config.toml` ou `dashboard.py`:
- **Automático**: Streamlit detecta mudanças no `.py` e recarrega
- **Manual**: Pressione `R` na aba do navegador ou `Ctrl+C` + `streamlit run`

## 10. Exemplo Completo: Layout Wide + Tema Escuro

**dashboard.py (início):**
```python
import streamlit as st

st.set_page_config(page_title="TCCs UFRR", layout="wide", page_icon="📚")

st.markdown("""
<style>
    h1 { text-align: center; color: #4AABDB; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Corpus de TCCs — LIDAE/UFRR")
```

**.streamlit/config.toml:**
```toml
[theme]
darkMode = true
primaryColor = "#4AABDB"
```

---

**Dúvidas?** Edite o arquivo e recarregue — Streamlit aplica mudanças em tempo real.

# Guia Completo — Reimportação e Publicação do Dashboard

## Índice

1. [Reimportação de tipo_tcc](#1-reimportação-de-tipo_tcc)
2. [Publicação na Nuvem (Streamlit Community Cloud)](#2-publicação-na-nuvem-streamlit-community-cloud)
3. [Troubleshooting](#3-troubleshooting)

---

## 1. Reimportação de tipo_tcc

### 1.1 Situação Atual

- **95 de 128 TCCs** têm `tipo_tcc` vazio
- Um arquivo de relatório foi gerado: `outputs/relatorio_tipo_tcc_vazio.xlsx`
- Um script de reimportação está pronto: `reimporta_tipo_tcc.py`

### 1.2 Passo a Passo para Preencher

#### Passo 1: Abra o relatório de TCCs vazios

```
corpus_v2/outputs/relatorio_tipo_tcc_vazio.xlsx
```

Colunas:
- `id` — identificador único (não edite)
- `grupo_tcc` — grupo de curso (não edite)
- `titulo` — título do TCC (use para identificar)
- `autor` — autor do trabalho (não edite)
- `orientador` — orientador (referência)
- `pesquisador` — **quem catalogou** ← contate esta pessoa
- `ano_defesa` — ano (não edite)
- `curso_fonte` — curso original (não edite)

#### Passo 2: Para cada linha, identifique o tipo

Para cada TCC:

1. Leia o título para se orientar
2. Clique no campo `link` (contém URL do Drive/localização)
3. Acesse o documento original
4. Procure pela informação de tipo:
   - Capa do trabalho
   - Ficha catalográfica
   - Ou pergunte ao pesquisador (`pesquisador`)

#### Passo 3: Tipos aceitos

Preencha com **UM DESTES**:

- `Monografia` — trabalho de conclusão de curso
- `Artigo` — artigo científico ou acadêmico
- `Relato de Experiência` — relato vivencial
- `Trabalho de Pesquisa` — pesquisa sistemática
- `Projeto` — projeto de intervenção
- `Dissertação` — nível mestrado
- `Tese` — nível doutorado
- `Estudo de Caso` — análise de caso específico
- `Revisão Sistemática` — revisão de literatura
- `Ensaio` — ensaio acadêmico
- `Resenha` — resenha crítica
- `Outro` — se não se encaixa em nenhum

#### Passo 4: Crie arquivo preenchido

**Opção A — Direto em Excel:**
1. Abra `relatorio_tipo_tcc_vazio.xlsx` novamente
2. Adicione uma **nova coluna** chamada `tipo_tcc`
3. Preencha as células com os tipos identificados
4. Salve como: **`relatorio_tipo_tcc_vazio_PREENCHIDO.xlsx`**

**Opção B — CSV simples:**
1. Crie um arquivo CSV com 2 colunas:
   ```
   id,tipo_tcc
   1,Monografia
   2,Artigo
   3,Relato de Experiência
   ...
   ```
2. Salve como: **`relatorio_tipo_tcc_vazio_PREENCHIDO.csv`**

### 1.3 Reimportar para a Base

#### Passo 1: Verifique o arquivo preenchido

Certifique-se de que:
- ✅ Tem coluna `id` (números inteiros: 1, 2, 3…)
- ✅ Tem coluna `tipo_tcc` (com os tipos preenchidos)
- ✅ Está em `.xlsx` ou `.csv`
- ✅ Está na pasta `corpus_v2/outputs/`

#### Passo 2: Execute o script

Abra o terminal, navegue até `corpus_v2` e execute:

```bash
cd corpus_v2
python3 reimporta_tipo_tcc.py outputs/relatorio_tipo_tcc_vazio_PREENCHIDO.xlsx
```

Ou, se for CSV:

```bash
python3 reimporta_tipo_tcc.py outputs/relatorio_tipo_tcc_vazio_PREENCHIDO.csv
```

#### Passo 3: Acompanhe o processo

O script mostrará:

```
┌────────────────────────────────────────────┐
│ REIMPORTAÇÃO DE TIPO_TCC - CORPUS LIDAE   │
└────────────────────────────────────────────┘

✓ Carregado: 95 registros
✓ Base original carregada: 128 registros
✓ Backup criado: outputs/backups/corpus_tccs_analisado_BACKUP_20260617_143022.csv
✓ Base atualizada: outputs/analise/corpus_tccs_analisado.csv
✓ Excel atualizado: outputs/analise/corpus_tccs_analisado.xlsx

RELATÓRIO DE REIMPORTAÇÃO
======================================================================
✓ Registros atualizados: 92

⚠️  Conflitos encontrados: 3
   (tipo_tcc já estava preenchido — mantido valor original)

📊 Resumo final:
   Total com tipo_tcc preenchido: 123/128
   Distribuição:
     - Monografia: 58
     - Artigo: 35
     - Relato de Experiência: 28
     - Outros: 2

✅ CONCLUÍDO COM SUCESSO!
```

#### Passo 4: Verifique no dashboard

Ao recarregar o dashboard (se estiver rodando):
- O filtro de tipos estará disponível
- Os gráficos refletirão os novos dados

### 1.4 Segurança e Backup

**Tudo é seguro:**
- 🔒 Backup automático antes de qualquer mudança
- 📂 Salvo em: `corpus_v2/outputs/backups/`
- ⏮️ Quer desfazer? Copie o backup de volta:
  ```bash
  cp outputs/backups/corpus_tccs_analisado_BACKUP_*.csv outputs/analise/corpus_tccs_analisado.csv
  ```

---

## 2. Publicação na Nuvem (Streamlit Community Cloud)

### 2.1 Por que publicar?

- 🌐 Dashboard acessível de qualquer lugar (sem rodar localmente)
- 🔓 Compartilhe com os pesquisadores (link único)
- 🆓 Totalmente gratuito (Streamlit Community Cloud)
- 📱 Funciona em desktop, tablet, celular

### 2.2 Pré-requisitos

1. **GitHub** — conta gratuita em https://github.com
2. **Streamlit Community Cloud** — conta gratuita em https://streamlit.io
3. **Este repositório** no seu GitHub pessoal

### 2.3 Passo 1: Preparar o repositório GitHub

#### 1a. Criar repositório no GitHub

1. Acesse https://github.com/new
2. Preencha:
   - **Repository name:** `corpus-tcc-lidae` (ou outro nome)
   - **Description:** "Dashboard interativo de TCCs — LIDAE/UFRR"
   - **Public** ← IMPORTANTE (precisa ser público para Community Cloud)
3. Clique em "Create repository"

#### 1b. Fazer upload dos arquivos

No terminal, dentro de `corpus_v2`:

```bash
# inicializar git (se não estiver iniciado)
git init

# adicionar todos os arquivos
git add .

# commit
git commit -m "Dashboard LIDAE corpus TCCs — v1.0"

# adicionar remote (use a URL do seu repositório)
git remote add origin https://github.com/seu_usuario/corpus-tcc-lidae.git

# push para GitHub
git branch -M main
git push -u origin main
```

### 2.4 Passo 2: Configurar Streamlit Community Cloud

#### 2a. Criar arquivo de dependências

No **raiz** de `corpus_v2`, crie um arquivo chamado `requirements.txt`:

```bash
streamlit==1.28.1
pandas==2.0.3
plotly==5.17.0
scikit-learn==1.3.2
fuzzywuzzy==0.18.0
python-Levenshtein==0.21.1
openpyxl==3.1.2
```

Salve e faça commit:

```bash
git add requirements.txt
git commit -m "Add dependencies for Cloud deployment"
git push
```

#### 2b. Fazer login no Streamlit Cloud

1. Acesse https://share.streamlit.io
2. Clique em "Sign in with GitHub"
3. Autorize o Streamlit Cloud a acessar seus repositórios

#### 2c. Deploy da aplicação

1. Após login, clique em "New app" (canto superior direito)
2. Preencha:
   - **Repository:** selecione `seu_usuario/corpus-tcc-lidae`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
3. Clique em "Deploy"

**⏳ Aguarde:**
- Instalação de dependências (~2-3 min)
- Build do dashboard (~1-2 min)

Quando terminar, você verá:
```
✓ App is ready to go
https://seu-app-name.streamlit.app
```

### 2.5 Passo 3: Configurar no Streamlit Cloud (opcional)

Para customizações avançadas:

1. Crie uma pasta `.streamlit` no raiz (mesma pasta de `dashboard.py`)
2. Crie um arquivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2C6E91"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"
```

3. Commit e push:

```bash
git add .streamlit/config.toml
git commit -m "Add Streamlit config for Cloud"
git push
```

4. O Streamlit Cloud detectará a mudança e **redeploy automaticamente** ✨

### 2.6 Compartilhar o Dashboard

**Link público:**
```
https://seu-app-name.streamlit.app
```

**Compartilhe com:**
- Pesquisadores
- Coordenadores de curso
- Orientadores
- Qualquer um com o link

**Ninguém precisa instalar nada!** Só acessar o link no navegador.

### 2.7 Atualizar após mudanças

Quando quiser atualizar (ex: novos dados, novo layout):

```bash
# faça as mudanças nos arquivos
# exemplo: edite dashboard.py

# commit e push
git add .
git commit -m "Update dashboard layout"
git push
```

O Streamlit Cloud detectará e **redeploy automaticamente** em ~30-60 segundos.

### 2.8 Monitoramento e Logs

No painel do Streamlit Cloud:
1. Clique no seu app
2. Abra a aba "Logs"
3. Veja erros e atividades em tempo real

---

## 3. Troubleshooting

### 3.1 Script de reimportação não funciona

**Erro: "No module named pandas"**
```bash
pip install pandas openpyxl
```

**Erro: "File not found"**
- Verifique o caminho do arquivo
- Certifique-se de estar na pasta `corpus_v2`

**Erro: "Invalid tipo_tcc"**
- Use um dos tipos da lista (veja seção 1.3)
- Sem acentuação (ou com, o script é flexível)

### 3.2 Dashboard não carrega na nuvem

**Erro: "ModuleNotFoundError"**
- Atualize `requirements.txt`
- Faça git push
- Aguarde o redeploy

**Erro: "File not found"**
- Verifique que `outputs/analise/corpus_tccs_analisado.csv` foi feito upload no GitHub
- Verifique os caminhos dos arquivos (devem ser relativos)

### 3.3 Dados não atualizam após reimportação

**Problema: Dashboard ainda mostra dados antigos**

Solução:
```bash
# limpe o cache do Streamlit
streamlit cache clear

# ou force redeploy no Cloud:
# - faça uma mudança trivial (ex: espaço)
# - commit e push
```

### 3.4 GitHub não está sincronizando

**Erro: "fatal: not a git repository"**
```bash
cd corpus_v2
git init
git remote add origin https://seu_repo
```

**Erro: "Permission denied"**
- Gere SSH key: `ssh-keygen -t ed25519`
- Adicione em GitHub: Settings → SSH Keys
- Use URL SSH: `git@github.com:usuario/repo.git`

---

## 4. Checklist Final

Antes de considerar tudo pronto:

### Reimportação
- ✅ Preencheu `tipo_tcc` para os 95 TCCs
- ✅ Criou arquivo `relatorio_tipo_tcc_vazio_PREENCHIDO.xlsx` ou `.csv`
- ✅ Executou `python3 reimporta_tipo_tcc.py` com sucesso
- ✅ Viu mensagem "✅ CONCLUÍDO COM SUCESSO!"
- ✅ Backup foi criado em `outputs/backups/`

### Publicação
- ✅ Repositório GitHub criado e público
- ✅ Todos os arquivos fazem commit e push
- ✅ `requirements.txt` está presente
- ✅ Dashboard faz deploy no Streamlit Cloud
- ✅ Link público funciona (`https://seu-app.streamlit.app`)
- ✅ Dados aparecem corretamente

### Compartilhamento
- ✅ Compartilhei o link com pesquisadores/coordenadores
- ✅ Testei em celular/tablet também
- ✅ Documentei os próximos passos de manutenção

---

## 5. Manutenção Futura

### Atualizar dados periodicamente

Quando novos TCCs forem catalogados:

1. Regenerar a análise:
   ```bash
   python3 analise_corpus.py
   ```

2. Dashboard atualiza automaticamente (se na nuvem)

### Customizações

Para mudar cores, layout, etc:
- Edite `dashboard.py`
- Edite `.streamlit/config.toml`
- Commit, push, redeploy automático

### Backup de dados

Mantenha `outputs/backups/` no GitHub para ter histórico.

---

## 6. Dúvidas Frequentes

**P: Qual é a segurança dos dados?**
A: Todos em repositório GitHub (privado recomendado se tiver dados sensíveis). Dashboard é read-only, ninguém edita via web.

**P: Streamlit Cloud tem limite de dados?**
A: Limite gratuito: 3 apps simultâneos. Seu corpus é pequeno (~1MB), sem problemas.

**P: E se o GitHub ficar offline?**
A: Dashboard fica offline também (precisa do Git). Recomendo: backup local + outro Git (GitLab, Gitea).

**P: Posso customizar mais o dashboard?**
A: Sim! Edite `dashboard.py`. Streamlit é muito flexível. Veja docs em https://docs.streamlit.io

---

**Pronto para começar?** 🚀

1. Preencha os 95 TCCs
2. Execute `reimporta_tipo_tcc.py`
3. Faça deploy no Streamlit Cloud
4. Compartilhe o link

Qualquer dúvida, consulte este guia!

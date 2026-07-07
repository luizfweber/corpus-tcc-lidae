# Protocolo de recebimento e tratamento de novos dados de TCCs

> Procedimento padrão sempre que chegar uma nova parte da catalogação (uma nova
> exportação do formulário Google Forms, em CSV). Redigido sem travessões.
> Objetivo: importar só o que é novo, limpar a nomenclatura de professores e
> bancas como já vínhamos fazendo, e nunca duplicar dados já cadastrados.

## Princípio

A parte MECÂNICA (detectar duplicatas, limpar nomes, unificar grafias, anexar)
é automatizada pelo script `importar_catalogacao.py`. A parte que exige
JULGAMENTO (revisar nomes sinalizados, re-curar rótulos de tópicos, categorizar
cursos novos) permanece com o pesquisador ou com a IA sob revisão, porque método
é instrumento de leitura, não veredito (CLAUDE.md §4).

## Passo a passo

### 1. Simular (não grava nada)

```
python3 importar_catalogacao.py "caminho/para/nova_catalogacao.csv"
```

O relatório mostra:
- Quantos já estavam cadastrados (ignorados) e quantos títulos eram URL (pulados).
- Quantos são NOVOS e sua distribuição por curso.
- Cursos sem mapeamento (entram como grupo próprio; avise se for curso inédito).
- Nomes a conferir: casamentos fuzzy no limiar (82 a 90 por cento), que PODEM ser
  a mesma pessoa. Conferir manualmente se são.
- Resíduos suspeitos: deve ser sempre 0. Se aparecer algo, ajustar o limpador
  antes de aplicar.

### 2. Conferir os nomes sinalizados

Para cada par sinalizado ("Fulano" ~ "Fulano de Tal", 86 por cento), decidir se é
a mesma pessoa. Se for, o script já mantém o nome novo separado; a unificação
definitiva pode ser feita depois com um pequeno mapa, ou aceita como pessoa nova.
Cuidado com homônimos que NÃO devem ser fundidos (ex.: Mariana Souza da Cunha do
Insikiran versus Mariana Cunha Pereira da História).

### 3. Aplicar (grava, com backup automático)

```
python3 importar_catalogacao.py "caminho/para/nova_catalogacao.csv" --aplicar
```

Isso faz backup do consolidado em `outputs/backups/` e anexa as linhas novas,
já limpas, com as colunas `banca_membro_1..4` geradas (orientador excluído).

### 4. Recalcular os modelos

```
python3 analise_corpus.py
```

Regenera o `corpus_tccs_analisado.csv` (lido pelo dashboard) com tópicos,
clusters e menção indígena para todo o corpus. Anote os termos dos tópicos que
o script imprime.

### 5. Re-curar os rótulos dos tópicos

Como o corpus mudou, os índices dos tópicos do LDA podem trocar. Atualizar o
dicionário `TOPICOS` no `dashboard.py` a partir dos termos impressos no passo 4.
Os rótulos são provisórios e pedem leitura qualitativa.

### 6. Categorizar cursos novos na análise por curso

Se entrou um curso inédito (ex.: Ciências Biológicas), incluí-lo em
`analise_por_curso.py` na camada certa (LDA, descritivo ou listagem, conforme o
N) e rodar:

```
python3 analise_por_curso.py
```

### 7. Validar

- Contagem igual entre analisado e consolidado.
- Nenhuma coluna com sufixo `.1` (lixo de merge).
- Habilitações resolvem sem cair no fallback (LEDUCARR, Insikiran, Letras).
- Zero nomes de banca suspeitos.
- Anos plausíveis (o pipeline já descarta fora de 1990 a 2030).
- Novos TCCs com tópico e cluster preenchidos.

### 8. Reiniciar o dashboard e publicar

```
streamlit run dashboard.py
```

Conferir no navegador. Depois, commit e push na branch main (auto-redeploy no
Streamlit Cloud). Deixar de fora do versionamento os backups e os relatórios
xlsx temporários.

## O que a limpeza faz com os nomes (resumo)

- Bancas viram formato "Nome | Nome | Nome".
- Remove títulos (Prof., Dr., Dra., Me., Msc.), inclusive com ordinal colado
  (Profº, Drª); funções (Orientador, Membro, Presidente); instituições (UFRR,
  Curso de..., Universidade); parênteses; e vazamentos de "Palavras-chave".
- Preserva acentos na grafia final; a chave sem acento serve só para agrupar.
- Unifica cada nome novo com os nomes canônicos já existentes por similaridade
  (fuzzy matching), resolvendo truncamentos, inversões e variações de acento.
- Gera as colunas por membro, com o orientador sempre fora (ele fica só na
  coluna orientador).

## Arquivos do protocolo

- `importar_catalogacao.py`: executa os passos 1 a 3 (mecânicos).
- `PROTOCOLO_DADOS.md`: este documento.
- `RELATORIO_DESENVOLVIMENTO.md`: contexto e histórico completo do projeto.

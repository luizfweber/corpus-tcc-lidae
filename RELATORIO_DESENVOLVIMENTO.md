# Relatório de Desenvolvimento: Painel de TCCs LIDAE/UFRR

> Documento didático que reúne tudo o que foi desenvolvido nesta linha de
> trabalho, para servir de material de ensino a uma IA (ou a novos colaboradores).
> Redigido sem travessões, conforme preferência do projeto.
> Estado final descrito aqui: corpus de 252 TCCs, LDA com 8 tópicos, painel
> Streamlit publicado em produção.

## 1. Objetivo do projeto

Construir e manter um painel interativo (Streamlit) que analisa, de forma
exploratória, o corpus de Trabalhos de Conclusão de Curso (TCCs) das licenciaturas
da UFRR, no âmbito do LIDAE (Laboratório de Indicadores, Dados e Analítica
Educacional) e do Observatório Roraimense da Formação Docente. A pergunta central
do sub-repositório é a cobertura da coleta de TCCs por curso frente ao universo de
egressos, mas o painel evoluiu para mapear temas, redes de orientação e bancas,
presença de temáticas indígenas e a produção por curso.

## 2. Princípios metodológicos (não negociáveis)

Estes princípios guiaram todas as decisões e devem ser preservados:

1. Exploratório, não censitário. Todo número é indício a interpretar, não conclusão.
2. Nunca imputar dados ausentes. Ano, curso, páginas ou banca faltantes são
   marcados e excluídos da estatística específica, jamais preenchidos por estimativa.
3. Preservar discrepâncias da fonte e nunca corrigir em silêncio. Quando os dados
   não fecham, registram-se os dois números e sinaliza-se.
4. Método é instrumento de leitura, não veredito. Não se afirma causa a partir de
   correlação, nem categoria sociológica a partir de cluster, nem tendência de
   produção a partir de disponibilidade de acervo.
5. Sempre declarar como cada número foi obtido (denominador, recorte, exclusões).
6. Nomes canônicos. Cursos e pessoas são normalizados antes de qualquer contagem;
   a normalização usa uma chave sem acento e sem caixa apenas para agrupar, e a
   exibição preserva a grafia mais frequente (com acentos).
7. Mediana, não média, para extensão de documentos (forte assimetria).

## 3. Arquitetura de dados e pipeline

Fluxo de dados em duas camadas, na pasta `corpus_v2`:

- Fonte: `outputs/corpus_tccs_consolidado.csv`. Contém as colunas de origem mais as
  colunas materializadas de banca separada (`banca_membro_1..4`).
- Enriquecido: `outputs/analise/corpus_tccs_analisado.csv`. É o arquivo que o
  dashboard lê. É gerado pelo pipeline a partir do consolidado.

Scripts principais:

- `analise_corpus.py`: lê o consolidado, faz limpeza textual, roda LDA (tópicos),
  clustering (k-means) e detecção de menção indígena, e grava o analisado com as
  colunas derivadas (`ano_num`, `pag_num`, `topico_dom`, `topico_prob`, `cluster`,
  `tem_indigena`). Também gera PNGs de relatório e o `relatorio_exploratorio.txt`.
- `analise_por_curso.py`: gera `analise_por_curso.json`, com uma análise em camadas
  por curso (LDA intra-curso, descritiva ou apenas listagem, conforme o N).
- `dashboard.py`: o painel Streamlit. Lê o analisado e o JSON por curso.

Regra de ouro do pipeline: ele escreve `colunas_de_origem (do consolidado) + campos_novos`.
Por isso, qualquer coluna que precise sobreviver a um reprocessamento deve estar no
consolidado. E qualquer coluna que o pipeline recalcula NÃO deve estar duplicada no
consolidado, senão surgem colunas com sufixo `.1` (lixo de merge).

## 4. Evolução do corpus

O corpus cresceu em três momentos, sempre a partir de exportações do formulário de
catalogação (Google Forms), com a mesma estrutura de colunas:

- 145 TCCs: base inicial.
- 211 TCCs: importação de 66 novos (arquivo do formulário 1).
- 252 TCCs: importação de 41 novos (catalogação de 26/06/2026), que trouxe dois
  cursos ou habilitações inéditos: Ciências Biológicas (10) e LEDUCARR Ciências da
  Natureza e Matemática (6).

Distribuição final por curso: Insikiran 81, História 69, Pedagogia 29, Música 22,
LEDUCARR 16, Matemática 15, Letras 10, Ciências Biológicas 10.

Como identificar o que é novo: comparar o título normalizado (minúsculas, sem
acento, espaços colapsados) contra os títulos já na base. Pular linhas cujo título
é uma URL (campo preenchido errado). O restante são inserções.

## 5. Convenções de limpeza de dados (o coração do trabalho)

Esta seção é a mais importante para ensinar a IA. O corpus vem de texto livre
digitado por catalogadores, com grande variação. A qualidade das análises depende
inteiramente de normalizar bem.

### 5.1 Bancas examinadoras

Problema: o campo "Membros da banca examinadora" é texto livre, com separadores
inconsistentes (ponto e vírgula, vírgula, quebra de linha, a conjunção "e"),
títulos (Prof., Dr., Dra., Me., Msc.), funções (Orientador, Membro, Presidente,
Titular, Suplente), instituições (UFRR, Curso de..., Universidade), parênteses,
resíduos de abreviação com o caractere ordinal (Drº, Profª que viram "º" e "ª"
soltos), e até vazamento de outros campos (o texto "Palavras-chave" entrando na
banca).

Solução, um separador canônico com barra vertical:

- Formato final do campo `banca_examinadora`: `Nome 1 | Nome 2 | Nome 3`.
- Parsing por entrada: detecta o separador presente (`;`, quebra de linha, vírgula
  ou ponto) e divide.
- Limpeza de cada nome: remove título no início, corta em funções e instituições
  (dois pontos, hífen, "Curso de", "Universidade", parênteses), remove resíduos
  ordinais soltos, e aplica Title Case preservando conectivos (de, da, do, dos, e)
  em minúscula.
- Colunas materializadas: `banca_membro_1..4`, uma por avaliador, com o ORIENTADOR
  EXCLUÍDO (ele fica só na coluna `orientador`). A comparação para excluir o
  orientador é feita pela chave sem acento e sem caixa.

Convenção importante: em cada banca, o presidente/orientador conta como orientador,
não como membro. As análises de "membros" e a rede de co-participação usam apenas
`banca_membro_*`.

### 5.2 Orientadores e nomes de pessoas

- Nomes canônicos com acentos preservados na exibição. A remoção de acento serve
  apenas para agrupar variações.
- Unificação de variações do mesmo professor: caixa (LEUDA vs Leuda), acentos
  (Virginia vs Virgínia), erros de digitação (Magoli vs Mangoli, Michel vs Michael),
  truncamentos (Catarina Padilha vs Catarina Janira Padilha), inversões de nome
  (Cardoso de Sousa vs de Sousa Cardoso).
- Cuidado com homônimos que NÃO devem ser fundidos. Exemplo real: Mariana Souza da
  Cunha (Insikiran) e Mariana Cunha Pereira (História) são pessoas diferentes.
- Técnica poderosa para novas importações: após limpar um nome novo, casá-lo por
  fuzzy matching (token_sort_ratio, limiar em torno de 90) contra o conjunto de
  nomes canônicos já existentes na base. Isso resolve truncamentos e inversões
  automaticamente, sem mapa manual, e mantém consistência entre orientadores e
  membros de banca.
- No dashboard, `limpa_nome` faz a limpeza de exibição e `consolida_nomes` agrupa
  por similaridade em tempo de execução.

### 5.3 Palavras-chave

- Mantidas como texto livre no campo original, mas com colunas derivadas separadas
  quando necessário (uma palavra-chave por coluna), com detecção do separador por
  entrada e remoção do rótulo "Palavras-chave:" embutido.
- Para alimentar o LDA e o clustering, as palavras-chave são limpas (rótulo
  removido) antes de entrarem no texto. Sem isso, o token "palavras" e "chave"
  entram como ruído no modelo (afetava cerca de 22 TCCs).

### 5.4 Cursos e habilitações

- Cursos agregados em `grupo_tcc` (Insikiran, LEDUCARR, Letras) têm habilitação
  distinta no campo `curso_fonte`. A função `curso_habilitacao` no dashboard
  desagrega para exibição (coluna `curso_det`).
- LEDUCARR se escreve com dois R. Uma exportação trouxe "LEDUCAR"; padronizou-se
  tudo para "LEDUCARR" nos CSVs, nos arquivos de egressos e no dashboard.
- Egressos "habilitação não informada" foram removidos do seletor de cobertura por
  habilitação, pois não são atribuíveis a uma habilitação específica.
- Cursos novos (como Ciências Biológicas) entram automaticamente porque a ordem de
  cursos no dashboard é dinâmica (`value_counts`). Só é preciso categorizá-los na
  análise por curso (camada LDA, descritiva ou listagem, conforme o N).

### 5.5 Correções pontuais preservando a fonte

- Erros claros de digitação foram corrigidos e registrados. Exemplo: um TCC do
  LEDUCARR com "2024" no campo de páginas era o ano, e foi corrigido para 24 após
  conferência no PDF.
- Quando um valor é implausível e não se pode confirmar, marca-se como ausente e
  exclui-se da estatística, em vez de imputar.

## 6. Técnicas de análise

1. Modelagem de tópicos (LDA): sobre título mais resumo mais palavras-chave limpas.
   O número de tópicos K foi fixado em 8 por decisão de leitura, porque revela
   nichos interpretáveis (história e gênero, plantas medicinais, educação escolar
   indígena) que um K menor esconde. A perplexidade é registrada como indício, não
   como veredito. Os rótulos dos tópicos são provisórios e re-curados a cada
   re-treino, porque os índices dos tópicos mudam quando o corpus cresce.
2. Clustering (TF-IDF mais k-means): K escolhido por silhueta. Atenção: a silhueta
   usa amostragem sem semente fixa, então o K pode variar entre execuções. Isso é
   uma instabilidade conhecida do pipeline.
3. Redução de dimensionalidade (TruncatedSVD) para projetar em 2D e visualizar
   clusters.
4. Redes: co-participação entre membros de banca (sem o orientador), relação
   bipartite orientador versus membros convidados, rede de orientação por tópico e
   co-ocorrência de palavras-chave. Layout de força (spring layout), tamanho do nó
   pela frequência, cor por tipo de nó quando bipartite.
5. Detecção de menção indígena por dicionário regional (gazetteer): lista de termos
   (povos, territórios, termos gerais) buscada em título mais resumo mais
   palavras-chave, sem inferência. A lista foi expandida com os povos e territórios
   de Roraima e com "comunidade raposa". O termo "maloca" foi deliberadamente
   excluído por ser ambíguo (gerou falso positivo em um projeto escolar não
   indígena). Resultado final: 117 de 252 TCCs com menção.
6. Consolidação de nomes por fuzzy matching (rapidfuzz, token_sort_ratio).
7. Estatística descritiva: distribuições por curso e ano, mediana de páginas,
   cobertura frente aos egressos (fonte PROEG).
8. Análise temática qualitativa: para cursos com N pequeno, leitura sistemática dos
   TCCs, agrupando-os em eixos. Feita para Música, as três habilitações do
   Insikiran, Pedagogia e História. Cada análise vive em um arquivo
   `analise_tematica_*.md` e é exibida no dashboard, com um gráfico de eixos e o
   texto de metodologia.

Distinção fundamental que o painel deixa clara: a aba de Tópicos usa algoritmo
(LDA sobre todo o corpus); a aba de Análise temática por curso usa leitura humana.
São instrumentos diferentes, ambos exploratórios.

## 7. O dashboard (Streamlit)

- Navegação lateral por seções, agrupadas em blocos (Panorama, Temas e conteúdo,
  Presença indígena, Pessoas e redes).
- Seções principais: Distribuição, Tópicos (LDA), Sub-temas por curso (LDA),
  Menção indígena, Orientadores, Explorar TCCs, Cobertura de Coleta, Povos e
  territórios, Palavras-chave, Bancas, Orientador versus tema, Análise temática por
  curso.
- Filtros na barra lateral: curso com habilitações, ano, apenas com menção
  indígena, apenas com banca cadastrada. Todos os números recalculam pelo filtro,
  e o denominador é sempre os TCCs selecionados.
- Padrão de "o que está faltando": um helper `lista_faltando` mostra, num expander,
  os TCCs sem determinado campo cadastrado (orientador, ano, páginas, banca,
  palavras-chave), sempre com a nota de que ausência é lacuna de coleta, não
  inexistência.
- Textos de metodologia e de interpretação acompanham as visualizações mais
  complexas (LDA e redes de banca), explicando como foram construídas e como ler.
- Apresentações escolhidas por adequação ao dado: gráficos de barras para
  contagens, heatmap para tópico versus curso, treemap para o esforço de
  catalogação por pesquisador (dado muito concentrado), redes para relações.

## 8. Bugs encontrados e lições de engenharia

1. Cache que não invalidava. As funções `carregar` e `carregar_por_curso` usavam
   um parâmetro `_mtime` com underscore. No `st.cache_data`, parâmetros com
   underscore são ignorados na chave do cache. Resultado: o cache nunca invalidava
   e a nuvem podia servir dados antigos (os tópicos não atualizavam). Correção:
   renomear para `mtime`, sem underscore, para que a mudança do arquivo invalide o
   cache. Lição: em Streamlit, para invalidar cache por mudança de arquivo, o
   parâmetro de mtime não pode ter underscore.
2. Seleção fixa de tópicos. A página Orientador versus tema montava a matriz com
   `range(4)`, herança de quando K era 4, e escondia os tópicos 4 a 7 com K igual a
   8. Correção: usar `range(len(TOPICOS))`. Lição: nunca fixar o número de tópicos
   em constantes espalhadas; derivar sempre do dicionário de rótulos.
3. Colunas fantasma `.1`. O pipeline escreve colunas de origem mais campos novos.
   Quando o consolidado já continha uma coluna que o pipeline recalcula, surgia um
   duplicata com sufixo `.1`. Correção: reconstruir o consolidado só com colunas de
   origem verdadeiras antes de rodar o pipeline.
4. Regex de título corrompendo nomes. Tokens curtos como "Ma", "Me", "Dr" sem
   fronteira de palavra correta cortavam nomes reais (Mendoza virava Ndoza, Maria
   virava ria). Lição: para stripping de títulos exigir fronteira de palavra
   completa, e para casos difíceis preferir mapa explícito a regex agressiva.
5. Não determinismo do clustering. A silhueta amostra sem semente fixa, então o K
   de cluster pode mudar entre execuções. É uma fragilidade a monitorar; se
   precisar de reprodutibilidade total, fixar a semente da amostragem.

## 9. Receita para atualizar o banco com um novo arquivo de catalogação

Passo a passo consolidado nesta sessão, que deve ser seguido em futuras importações:

1. Ler o novo CSV (mesma estrutura do formulário). Identificar os novos por título
   normalizado versus a base. Pular títulos que são URL.
2. Mapear curso para `grupo_tcc` e `curso_fonte`, aplicando LEDUCAR para LEDUCARR.
   Cursos novos entram como novo grupo.
3. Limpar a banca para o formato com barra vertical e nomes canônicos, e unificar
   por fuzzy matching contra os nomes já existentes na base. Gerar
   `banca_membro_1..4` excluindo o orientador.
4. Limpar o orientador (remover títulos, corrigir caixa) e unificar por fuzzy.
5. Fazer backup do consolidado. Anexar as novas linhas ao consolidado, com todas as
   colunas de origem mais `banca_membro_*`.
6. Rodar `analise_corpus.py` para recalcular ano, páginas, tópicos, clusters e
   menção indígena para todo o corpus. Isso regenera o analisado preservando as
   colunas de origem.
7. Re-curar os rótulos dos tópicos no dicionário TOPICOS do dashboard, a partir dos
   termos que o pipeline imprime, porque os índices mudam.
8. Categorizar cursos novos em `analise_por_curso.py` (camada LDA, descritiva ou
   listagem) e rodá-lo.
9. Validar integridade: contagem igual entre analisado e consolidado, ausência de
   colunas `.1`, habilitações resolvem sem cair no fallback, zero nomes de banca
   suspeitos, novos com tópico e cluster preenchidos.
10. Reiniciar o dashboard local, conferir, e publicar.

## 10. Publicação (deploy)

- O deploy é por push na branch main do repositório GitHub luizfweber/corpus-tcc-lidae,
  que dispara auto-redeploy no Streamlit Cloud.
- Publicar apenas os arquivos necessários. Ficam de fora do versionamento os
  backups de trabalho e os relatórios xlsx temporários.
- Mensagens de commit terminam com a linha de coautoria.
- Se a nuvem parecer presa em versão antiga (histórico do cache anterior à
  correção), um Reboot app resolve uma única vez.

## 11. Arquivos-chave

- `dashboard.py`: o painel. Contém TOPICOS (rótulos), o gazetteer, os helpers de
  limpeza de nome e de banca, e as seções.
- `analise_corpus.py`: pipeline de LDA, clusters e menção indígena.
- `analise_por_curso.py`: análise em camadas por curso.
- `outputs/corpus_tccs_consolidado.csv`: fonte.
- `outputs/analise/corpus_tccs_analisado.csv`: enriquecido, lido pelo dashboard.
- `dados/egressos_*.csv`: séries de egressos (fonte PROEG) para a cobertura.
- `outputs/analise/analise_tematica_*.md`: leituras temáticas qualitativas.
- `SOBRE_LIDAE.md`: texto institucional para uma futura seção.

## 12. Lições transferíveis para uma IA

1. A limpeza de dados de texto livre é o trabalho central e mais custoso. Priorize
   normalização canônica antes de qualquer estatística.
2. Prefira mapas explícitos e verificáveis a regex agressiva quando o volume é
   pequeno e os erros são caros.
3. Use fuzzy matching contra um conjunto canônico existente para unificar novas
   entradas sem re-fazer trabalho manual.
4. Trate modelos (LDA, clusters) como instrumentos exploratórios. Rótulos são
   provisórios; registre a incerteza (perplexidade, silhueta, estabilidade por ARI).
5. Nunca impute dado ausente. Marque, exclua da estatística específica e mostre a
   lacuna com transparência.
6. Ao materializar colunas derivadas num pipeline idempotente, decida conscientemente
   se elas vivem na fonte ou são recalculadas, para evitar duplicatas e perdas.
7. Documente como cada número foi obtido. O painel repete, em cada visão, o
   denominador e as exclusões.
8. Ao publicar, entenda o mecanismo de cache do ambiente. Um parâmetro mal nomeado
   pode congelar dados antigos em produção.

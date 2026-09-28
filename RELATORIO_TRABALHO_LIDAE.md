# Relatório do trabalho desenvolvido: LIDAE/NECPF (UFRR)

> Observatório Roraimense da Formação Docente. Laboratório de Indicadores, Dados
> e Analítica Educacional (LIDAE), operado no NECPF/UFRR, em cooperação
> UFRR-UNMdP, projeto PROSUL/CNPq. Panorama do que já foi construído até
> 10/07/2026. Documento exploratório: os números são indícios a interpretar, não
> conclusões (metodologia LIDAE).

## 1. Objeto e pergunta

O laboratório estuda a **formação docente** nas licenciaturas da UFRR por meio de
**Mineração de Dados Educacionais (EDM)** sobre um corpus de TCCs e dos projetos
pedagógicos dos cursos. Este eixo do trabalho responde a uma pergunta central:
dado o universo de **egressos** das licenciaturas, **qual a cobertura da coleta de
TCCs por curso** e o que esse acervo revela sobre temas, orientações e bancas.

## 2. O que já foi construído (visão geral)

1. Um **corpus estruturado** de TCCs, catalogado pela equipe e consolidado num
   pipeline reproduzível.
2. Um **pipeline de análise** (tópicos, agrupamentos, redes, menção indígena,
   estatística descritiva) idempotente, que regenera todos os resultados a partir
   das fontes.
3. Um **painel interativo** (dashboard) público que torna os indicadores
   acessíveis, com identidade visual do NECPF.
4. Um **protocolo de dados** para receber, limpar e deduplicar novas catalogações
   sem perder rastreabilidade.
5. A **integração da base de egressos** da UFRR (DTI), com tratamento de LGPD,
   permitindo a análise de cobertura por curso.
6. **Análises temáticas qualitativas** por curso, complementares aos métodos
   estatísticos.

## 3. Corpus de TCCs (números atuais)

- **321 TCCs** catalogados, de **8 cursos** com coleta.
- Distribuição por grupo de curso: História 122, Insikiran 87, Pedagogia 29,
  Música 22, Ciências Biológicas 20, LEDUCARR 16, Matemática 15, Letras 10.
- **136 dos 321** (42%) têm menção a povos, territórios ou saberes indígenas.
- Seis cursos ainda com **zero TCCs** coletados (Geografia, Química, Física,
  Artes Visuais, e as lacunas remanescentes), sinalizando a maior frente de
  coleta a preencher.

Cada TCC guarda título, autoria, orientação, banca examinadora, ano e semestre,
páginas, palavras-chave, resumo e observações do pesquisador, além dos campos
enriquecidos pela análise (tópico, cluster, menção indígena).

## 4. Base de egressos e cobertura da coleta

Em 10/07/2026 o laboratório recebeu da **DTI/UFRR** a base individual de egressos
(15.428 registros da UFRR inteira; 5.273 egressos distintos das licenciaturas do
estudo, após deduplicação por matrícula e exclusão de bacharelado e EaD).

Sobre ela foi calculada a **cobertura por curso** (TCCs coletados divididos por
egressos), com janela padrão 2015-2025:

- Cobertura global na janela: cerca de **18,6%**.
- Mais profunda em **História (56%)** e **Música (48%)**, onde a coleta concentrou
  esforço; mais rasa ou nula nos cursos ainda não coletados.

Achado relevante: em vários cursos o acervo do NECPF **supera o registro oficial**
(ex.: História tem 122 TCCs catalogados frente a poucas dezenas de títulos
registrados no sistema da universidade).

### Tratamento de dados pessoais (LGPD)

A base da DTI contém nome e matrícula. O laboratório adotou **proteção parcial**:
nome, curso, período e título podem ser públicos (TCCs são documentos públicos),
mas **matrícula e histórico de matrículas ficam protegidos** e nunca são
divulgados. Na prática, os dados sensíveis ficam numa área restrita, e todo
arquivo ou painel público é gerado sem eles.

## 5. Métodos e técnicas

**Principais**
1. Modelagem de tópicos (LDA) sobre título, resumo e palavras-chave (nível global
   e sub-temas por curso).
2. Agrupamento (TF-IDF + K-means) por semelhança de vocabulário.
3. Análise de redes: co-participação em bancas, relação orientador-avaliadores,
   co-ocorrência de palavras-chave.
4. Detecção por dicionário regional (gazetteer) de povos e territórios indígenas
   de Roraima.
5. Consolidação de nomes por similaridade (fuzzy matching) de orientadores,
   pesquisadores e membros de banca.
6. Estatística descritiva: distribuições por curso e ano, mediana de páginas
   (não média, pela assimetria), cobertura frente aos egressos.
7. Análise temática qualitativa por leitura, para cursos com volume pequeno.

**De apoio**: pré-processamento textual (NLP), vetorização (CountVectorizer,
TF-IDF), validação de modelos (perplexidade, silhueta, estabilidade por ARI),
redução de dimensionalidade (TruncatedSVD), layout de força para redes, e
estruturação de campos de texto livre.

## 6. Produtos entregues

- **Dashboard público** (Streamlit) com abas de distribuição, cobertura de coleta,
  registros faltantes por curso, tópicos (LDA), análise e sub-temas por curso,
  palavras-chave, menção indígena, povos e territórios, orientadores, bancas e a
  relação orientador-tema.
- **Pipeline reproduzível** (importação, análise do corpus, análise por curso) com
  saídas versionadas (CSV, gráficos, relatórios).
- **Protocolo de dados** documentado: recepção, limpeza de nomes e banca,
  detecção de duplicatas e trilha de auditoria (backups datados).
- **Análises temáticas** por curso (História, Insikiran/Ciências da Natureza,
  Música, Ciências Biológicas), por leitura sistemática.
- **Formulário de catalogação** (Google Forms) padronizado, hoje na v3, com
  proposta de revisão v4 em discussão (banca campo a campo, matrícula para
  vínculo com egressos, validações).
- **Ferramenta de registros faltantes**: cruza egressos e TCCs coletados e lista,
  por curso e período, quem ainda não tem TCC catalogado, orientando a coleta.

## 7. Princípios metodológicos

- **Exploratório, não censitário**: todo número é indício a interpretar.
- **Nunca imputar** dados ausentes; ausências são marcadas e excluídas da
  estatística específica.
- **Preservar discrepâncias** da fonte, registrando os dois números quando não
  fecham, sem "corrigir" em silêncio.
- **Método é instrumento de leitura, não veredito**: não se afirma causa a partir
  de correlação, nem categoria social a partir de cluster, nem tendência de
  produção a partir de disponibilidade de acervo.
- **Sempre declarar** como cada número foi obtido (denominador, recorte, exclusões).

## 8. Estado atual e próximos passos

**Consolidado**: corpus de 321 TCCs, pipeline reproduzível, dashboard público,
protocolo de importação, base de egressos integrada com cobertura por curso e
proteção de dados pessoais.

**Em andamento / próximos**
- Preencher a coleta dos cursos ainda sem TCCs (Geografia, Química, Física, Artes
  Visuais e demais lacunas), guiada pela aba de registros faltantes.
- Revisão do formulário para a v4 (banca campo a campo; matrícula opcional para
  vínculo exato com egressos; validações de ano).
- Confirmar com a PROEG a definição de egresso e reconciliar os totais oficiais.
- Ampliar as análises temáticas qualitativas aos demais cursos conforme o volume.

---

*Relatório gerado em 10/07/2026 a partir do estado do repositório e das bases do
projeto. Números sujeitos a atualização conforme o corpus cresce.*

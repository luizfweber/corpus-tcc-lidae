# Sobre o LIDAE

> Conteúdo de referência para uma futura seção "Sobre o LIDAE" no dashboard.
> Redigido sem travessões, conforme preferência do projeto.
> Observação: descrições baseadas nas atividades visíveis do projeto. Se houver
> documento institucional oficial, ajustar para refletir o texto formal.

## Descrição breve (até 500 caracteres)

O LIDAE (Laboratório de Indicadores, Dados e Analítica Educacional) é um laboratório da Universidade Federal de Roraima dedicado à análise de dados educacionais. Reúne, organiza e interpreta informações sobre a formação de professores nas licenciaturas, produzindo indicadores sobre temas, orientações e bancas. Seu trabalho tem caráter exploratório: os números servem como apoio à leitura qualitativa dos pesquisadores, não como conclusões definitivas.

## Principais técnicas

1. Modelagem de tópicos (LDA): sobre título, resumo e palavras-chave dos TCCs, para sugerir os assuntos recorrentes (tópicos no nível global e sub-temas por curso).
2. Agrupamento (clustering): TF-IDF combinado com K-means, agrupando os TCCs por semelhança de vocabulário.
3. Análise de redes: grafos de co-participação entre membros de banca, relação entre orientador e seus avaliadores, e co-ocorrência de palavras-chave.
4. Detecção por dicionário regional (gazetteer): identificação de menções a povos e territórios indígenas de Roraima por busca de termos.
5. Consolidação de nomes (fuzzy matching): normalização de grafias de orientadores, pesquisadores e membros de banca por similaridade.
6. Estatística descritiva: distribuições por curso e ano, mediana de páginas e cobertura da coleta frente aos egressos.
7. Análise temática qualitativa: leitura sistemática dos trabalhos, por curso, agrupando-os em eixos quando o volume é pequeno para modelagem estatística.

### Técnicas de apoio

8. Pré-processamento textual (NLP): padronização para minúsculas, remoção de acentos, de palavras vazias e de termos genéricos, e filtro por tamanho mínimo de palavra.
9. Vetorização de texto: representação como saco de palavras (CountVectorizer) e ponderação TF-IDF.
10. Seleção e validação de modelos: perplexidade (LDA), silhueta (K-means) e estabilidade entre sementes pelo índice ARI.
11. Redução de dimensionalidade: TruncatedSVD para projetar os textos em duas dimensões e visualizar os clusters.
12. Layout de força para redes: algoritmo de mola (spring layout), que aproxima quem aparece junto com frequência.
13. Estruturação de texto livre: separação de campos escritos livremente (banca e palavras-chave) em colunas, com detecção do separador e remoção de títulos e instituições.

## Áreas de atuação

1. Formação docente nas licenciaturas: estudo da produção acadêmica dos cursos de formação de professores da UFRR, a partir de TCCs e dos projetos pedagógicos dos cursos.
2. Mineração de dados educacionais (EDM): técnicas computacionais para mapear temas e padrões na produção acadêmica.
3. Análise de redes acadêmicas: relações de orientação e de bancas examinadoras, identificando núcleos e colaborações por curso ou área.
4. Temáticas regionais e educação escolar indígena: presença de povos, territórios e saberes indígenas de Roraima na produção das licenciaturas.
5. Indicadores e cobertura de coleta: indicadores sobre o acervo, incluindo a cobertura dos TCCs coletados frente ao universo de egressos.
6. Análise temática qualitativa: leitura e organização dos trabalhos por eixos temáticos, complementando os métodos estatísticos.
7. Visualização de dados e painéis: painéis interativos que tornam os indicadores acessíveis para pesquisa e tomada de decisão.

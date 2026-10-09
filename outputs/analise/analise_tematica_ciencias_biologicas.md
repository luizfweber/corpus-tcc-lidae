# Análise temática: Ciências Biológicas (LIDAE/UFRR)

> Leitura descritiva e exploratória dos 25 TCCs do curso de Ciências Biológicas,
> a partir de título, resumo e palavras-chave. Fonte: cadastro dos TCCs realizado
> pelos pesquisadores do NECPF.
>
> Natureza da análise: agrupamento por leitura, é indício e não classificação
> fechada; os eixos podem se sobrepor.

## Como esta análise foi feita (método)

Esta é uma análise temática qualitativa, por leitura, não um agrupamento
automático. Os eixos não saíram de um algoritmo (como o LDA ou o k-means do
restante do painel); emergiram de uma leitura sistemática dos TCCs, apoiada por
contagem de termos. O passo a passo:

1. Reunião do material textual: para cada TCC, título mais resumo mais
   palavras-chave.
2. Apoio quantitativo: termos e palavras-chave mais repetidos, removendo palavras
   vazias e genéricas.
3. Leitura e codificação: foco central de cada TCC e um rótulo curto.
4. Agrupamento indutivo: os eixos emergiram do agrupamento, não foram definidos
   de antemão.
5. Nomeação de cada grupo.

Por que não LDA com N igual a 25? Porque é pequeno demais para modelagem estável
(o pipeline trata Ciências Biológicas na camada descritiva). A leitura humana é
mais confiável nessa escala, mas é interpretativa: outro leitor poderia agrupar de
forma ligeiramente diferente. Daí ser indício, não classificação fechada.

## Panorama

O curso reúne dois perfis: TCCs de pesquisa em biologia (taxonomia, biologia
molecular, epidemiologia, microbiologia ambiental) e TCCs de ensino de biologia
(recursos didáticos, jogos, sequências didáticas). Há forte presença de temas de
saúde pública regional (dengue, malária) e do ambiente amazônico (savana/lavrado,
qualidade da água).

## Eixos temáticos

Cada TCC entra em um único eixo, o do foco principal declarado no resumo.

### Eixo 1: Ensino de Biologia e recursos didáticos (10 TCCs)
Livros didáticos, jogos, sequências didáticas, informática e temas transversais no
ensino de biologia e ciências. Inclui educação ambiental com estudantes do ensino
fundamental (336) e o cultivo orgânico como estratégia educativa (337).
ids: 242, 247, 249, 250, 277, 278, 284, 285, 336, 337

### Eixo 2: Saúde, epidemiologia e bem-estar (6 TCCs)
Dengue (sorotipos, genótipos, vetor Aedes) e malária, com técnicas moleculares.
Inclui a epidemiologia do vírus Zika em Roraima (346) e a qualidade de vida e o
estresse de professores da rede estadual (335).
ids: 243, 244, 280, 282, 335, 346

### Eixo 3: Botânica, taxonomia e biodiversidade (4 TCCs)
Filogenia e taxonomia (aves, Polygalaceae), fungos do solo e biologia molecular do
guaraná, no ambiente de savana amazônica.
ids: 251, 276, 279, 283

### Eixo 4: Plantas medicinais, bioatividade e etnobiologia (3 TCCs)
Uso tradicional de plantas medicinais e atividade antioxidante e antimicrobiana de
extratos vegetais, incluindo fitoextratos de Melastomataceae (327).
ids: 241, 248, 327

### Eixo 5: Qualidade da água e ambiente (2 TCCs)
Potabilidade e qualidade microbiológica da água consumida no campus.
ids: 246, 281

**Conferência:** 10 + 6 + 4 + 3 + 2 = **25 TCCs**, igual ao total do curso no corpus.

## Leitura

Ciências Biológicas é o curso com o perfil mais próximo da pesquisa de bancada do
corpus: taxonomia, biologia molecular e epidemiologia convivem com uma frente de
ensino de biologia. Os temas de saúde (dengue, malária) e de ambiente (savana,
água) refletem agendas de pesquisa regionais de Roraima.

## Limites

- N igual a 25, com eixos pequenos: indício a confirmar por leitura.
- Há afinidade entre eixos (ex.: dengue aparece em epidemiologia e no ensino,
  como sequência didática). Cada TCC foi contado uma única vez.
- Reflete a coleta atual (cadastro NECPF), não o universo de TCCs do curso.

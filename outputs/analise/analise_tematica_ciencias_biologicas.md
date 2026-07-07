# Análise temática — Ciências Biológicas (LIDAE/UFRR)

> Leitura descritiva e exploratória dos 20 TCCs do curso de Ciências Biológicas,
> a partir de título, resumo e palavras-chave. Fonte: cadastro dos TCCs realizado
> pelos pesquisadores do NECPF.
>
> Natureza (CLAUDE.md §1): agrupamento por leitura, é indício e não classificação
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

Por que não LDA com N igual a 20? Porque é pequeno demais para modelagem estável
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

### Eixo 1 — Ensino de Biologia e recursos didáticos (8 TCCs)
Livros didáticos, jogos, sequências didáticas, informática e temas transversais no
ensino de biologia e ciências.
ids: 242, 247, 249, 250, 277, 278, 284, 285

### Eixo 2 — Saúde, arboviroses e epidemiologia (4 TCCs)
Dengue (sorotipos, genótipos, vetor Aedes) e malária, com técnicas moleculares.
ids: 243, 244, 280, 282

### Eixo 3 — Botânica, taxonomia e biodiversidade (4 TCCs)
Filogenia e taxonomia (aves, Polygalaceae), fungos do solo e biologia molecular do
guaraná, no ambiente de savana amazônica.
ids: 251, 276, 279, 283

### Eixo 4 — Etnobiologia e plantas medicinais (2 TCCs)
Uso tradicional de plantas medicinais e atividade antioxidante e antimicrobiana de
extratos vegetais.
ids: 241, 248

### Eixo 5 — Qualidade da água e ambiente (2 TCCs)
Potabilidade e qualidade microbiológica da água consumida no campus.
ids: 246, 281

## Leitura

Ciências Biológicas é o curso com o perfil mais próximo da pesquisa de bancada do
corpus: taxonomia, biologia molecular e epidemiologia convivem com uma frente de
ensino de biologia. Os temas de saúde (dengue, malária) e de ambiente (savana,
água) refletem agendas de pesquisa regionais de Roraima.

## Limites

- N igual a 20, com eixos pequenos: indício a confirmar por leitura.
- Os eixos podem se sobrepor (ex.: dengue aparece tanto em epidemiologia quanto no
  ensino, como sequência didática).
- Reflete a coleta atual (cadastro NECPF), não o universo de TCCs do curso.

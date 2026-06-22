# Análise temática — Pedagogia (LIDAE/UFRR)

> Leitura **descritiva e exploratória** dos 29 TCCs do curso de Pedagogia, a
> partir de **título + resumo + palavras-chave**. Fonte: cadastro dos TCCs
> realizado pelos pesquisadores do NECPF.
>
> **Natureza (CLAUDE.md §1):** agrupamento **por leitura**, é indício e não
> classificação fechada; os eixos podem se sobrepor.

## Como esta análise foi feita (método)

Esta é uma **análise temática qualitativa, por leitura** — não um agrupamento
automático. Os eixos **não** saíram de um algoritmo (como o LDA ou o k-means do
restante do painel); emergiram de uma leitura sistemática dos TCCs, apoiada por
contagem de termos. O passo a passo:

1. **Reunião do material textual.** Para cada TCC, juntei *título + resumo +
   palavras-chave*.
2. **Apoio quantitativo (frequência).** Calculei os termos e palavras-chave mais
   repetidos, removendo palavras vazias e genéricas ("trabalho", "pesquisa",
   "ensino", "escola"…). Isso evidenciou os fios dominantes.
3. **Leitura e codificação.** Li o **foco central** de cada TCC e atribuí um
   rótulo curto.
4. **Agrupamento indutivo.** Reuni os TCCs de foco semelhante; os eixos
   **emergiram** desse agrupamento, não foram definidos de antemão.
5. **Nomeação.** Cada grupo recebeu um nome que resume o foco comum.

**Por que não LDA com N = 29?** Porque é pequeno demais para uma modelagem
estatística estável (o pipeline trata Pedagogia na camada LDA intra-curso apenas
com K=2 e estabilidade baixa). Nessa escala a leitura humana é mais confiável —
mas é **interpretativa**: outro leitor poderia agrupar de forma ligeiramente
diferente. Daí ser **indício, não classificação fechada** (CLAUDE.md §1, §4).

## Panorama

Termos dominantes: *estágio* (45), *pedagogia* (43), *pedagógica* (38),
*formação* (36), *coordenação* (27), *infantil* (27), *experiência* (26),
*especial* (18), *supervisionado* (18). Palavras-chave mais repetidas: curso de
pedagogia (7), coordenação pedagógica (5), estágio curricular supervisionado (4),
educação infantil (3), educação especial (3), jogos (3).

O curso é fortemente marcado pelo **relato de experiência do estágio/residência**
e pela **gestão pedagógica**, com forte presença da educação infantil, da
educação especial e da atuação do pedagogo em contextos diversos.

## Eixos temáticos

### Eixo 1 — Estágio supervisionado e Residência Pedagógica (8 TCCs)
Relatos de experiência formadora no estágio e na Residência Pedagógica
(presencial, remoto, anos iniciais, alfabetização).
ids: 21, 23, 33, 34, 35, 44, 45, 47

### Eixo 2 — Coordenação e gestão pedagógica (6 TCCs)
Atuação e perfil do coordenador pedagógico, gestão escolar e relação
público-privado em Roraima.
ids: 22, 31, 36, 38, 39, 49

### Eixo 3 — Educação infantil, jogos e brincadeiras (4 TCCs)
Ludicidade, brincar e desenvolvimento na pré-escola e nos anos iniciais.
ids: 32, 40, 48, 149

### Eixo 4 — Educação especial e inclusão (4 TCCs)
Autismo/TEA, inclusão escolar e o ensino da educação especial nas licenciaturas.
ids: 20, 30, 113, 114

### Eixo 5 — Pedagogia em contextos não-escolares (4 TCCs)
Pedagogia hospitalar, pedagogo no judiciário e Educação de Jovens e Adultos.
ids: 42, 110, 111, 112

### Eixo 6 — Formação docente e educação indígena (3 TCCs · pontuais)
Formação de professores (normativa), configuração docente em comunidade
indígena e relato de vivência na educação escolar indígena.
ids: 37, 41, 43

## Leitura

A Pedagogia da UFRR aparece centrada na **prática profissional** — o estágio e a
residência são o gênero dominante — e na **gestão pedagógica**. Ao lado disso,
expande-se para **contextos não-escolares** (hospitalar, jurídico, EJA) e dá
atenção consistente à **educação especial/inclusão** e à educação infantil.

## Limites

- N = 29, com eixos pequenos — **indício a confirmar por leitura**.
- Os eixos podem se sobrepor (ex.: alfabetização aparece no estágio e na ed. infantil).
- Há TCCs de título idêntico (ids 32 e 149) — possível duplicata da fonte, mantida.
- Reflete **a coleta atual** (cadastro NECPF), não o universo de TCCs do curso.

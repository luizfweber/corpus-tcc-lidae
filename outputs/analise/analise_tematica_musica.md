# Análise temática — TCCs do curso de Música (LIDAE/UFRR)

> Leitura **descritiva e exploratória** dos 21 TCCs de Música do corpus
> (defesas de 2017 a 2025), a partir de **título + resumo + palavras-chave**.
> Fonte: cadastro dos TCCs realizado pelos pesquisadores do NECPF.
>
> **Natureza (CLAUDE.md §1):** com N = 21, não se aplica modelagem estatística
> de tópicos (o pipeline classifica Música na camada "descritiva", sem LDA
> intra-curso). O agrupamento abaixo é **por leitura**, é indício e não
> classificação fechada; os eixos **se sobrepõem**.

## Como esta análise foi feita (método)

Esta é uma **análise temática qualitativa, por leitura** — não um agrupamento
automático. Os 5 eixos **não** saíram de um algoritmo (como o LDA ou o k-means
usados no resto do painel); emergiram de uma leitura sistemática dos 21 TCCs,
apoiada por contagem de termos. O passo a passo:

1. **Reunião do material textual.** Para cada TCC, juntei *título + resumo +
   palavras-chave* (os campos solicitados).
2. **Apoio quantitativo (frequência).** Calculei quais termos e palavras-chave
   mais se repetem no conjunto, removendo palavras vazias e termos genéricos
   ("trabalho", "pesquisa", "educação", "ensino"…). Isso evidenciou os fios
   dominantes — educação musical, contexto roraimense/amazônico, prática docente
   — descritos no Panorama.
3. **Leitura e codificação.** Li o **foco central** de cada TCC (sobre o quê é o
   trabalho) e atribuí um rótulo curto a cada um.
4. **Agrupamento indutivo.** Reuni os TCCs de foco semelhante. Os eixos — e o
   próprio número **5** — **emergiram** desse agrupamento; não foram definidos
   de antemão. TCCs com mais de um foco ficaram marcados como transversais.
5. **Nomeação.** Cada grupo recebeu um nome que resume o foco comum.

**Por que não LDA/clusters aqui?** Porque N = 21 é pequeno demais para uma
modelagem estatística estável (por isso o pipeline coloca Música na camada
"descritiva", sem LDA intra-curso). Nessa escala, a leitura humana é mais
confiável — mas é **interpretativa**: outro leitor poderia agrupar de forma
ligeiramente diferente, e os eixos se sobrepõem. Daí serem **indício, não
classificação fechada** (CLAUDE.md §1, §4).

> Diferença em relação à aba "Tópicos (LDA)" do painel: lá, os tópicos são
> gerados por **algoritmo** sobre os 211 TCCs (K fixado em 8); aqui, os eixos
> são fruto de **leitura** dos 21 TCCs de Música — dois instrumentos distintos,
> ambos exploratórios.

## 1. Panorama

Dois fios atravessam quase todo o conjunto:

- **Educação musical** — "música/musical" aparece em 19/15 dos 21 TCCs;
  "educação musical" é a palavra-chave mais repetida (6×).
- **Contexto regional roraimense/amazônico** — "Boa Vista" (13×), "Roraima"
  (11×), "Amazônia" (2× nas palavras-chave).

A maioria parte de pesquisa empírica (entrevistas 8×; revisão bibliográfica 8×).

Palavras-chave repetidas (≥2 TCCs): educação musical (6), Roraima (3),
Amazônia (2), formação docente (2), aprendizagem informal (2), BNCC (2),
regência (2), inclusão (2).

## 2. Eixos temáticos

### Eixo 1 — Ensino de música na educação básica e formação docente (~8 TCCs)
O maior eixo: prática docente, estágio/Residência Pedagógica, BNCC e
referenciais de educação musical (Swanwick, Lucy Green).

- id 91 — aulas de música na educação básica (Residência Pedagógica; Swanwick)
- id 94 — práticas de canto e formação do licenciado
- id 98 — a regência nas aulas de música na educação básica
- id 85 — práticas informais de aprendizagem musical na formação (Lucy Green)
- id 86 — práticas de ensino na Residência Pedagógica (formação docente)
- id 212 — ensino remoto emergencial na pandemia (desafios da docência)
- id 87 — música × educação física: "O Passo", interdisciplinaridade (BNCC)
- id 95 — músicas regionalistas como material para o ensino (BNCC)

### Eixo 2 — Ensino de instrumentos e ensino coletivo (~4 TCCs)
- id 89 — aulas de piano em grupo (método Suzuki)
- id 83 — contrabaixo elétrico e gêneros musicais do Norte
- id 96 — ensino coletivo de violão (Orquestra de Violões do IBVM)
- id 109 — flauta doce com musicalidades indígenas roraimenses

### Eixo 3 — Música, cultura regional e identidade (~5 TCCs)
Festivais, percussão e memória: música como expressão cultural de
Roraima/Amazônia.

- id 84 — Festival Folclórico de Caracaraí
- id 97 — Festival Folclórico de Caracaraí: a percussão (Cobra Mariana, Gavião)
- id 95 — Festival Canto Forte: canções regionais
- id 82 — escolas de samba em Boa Vista (estudos de memória)
- id 83 — gêneros musicais do Norte (transversal ao Eixo 2)

### Eixo 4 — Música, religião e ritual (3 TCCs)
- id 108 — colaboração pianística no coro da Igreja Batista Regular de Boa Vista
- id 90 — canto coral na Igreja Batista Regular (ensino, regência)
- id 99 — música ritual no terreiro de Umbanda Ogum Matinata (Boa Vista)

### Eixo 5 — Educação musical, inclusão e políticas públicas (2 TCCs)
- id 93 — produção científica e políticas públicas de inclusão
- id 211 — produções científicas sobre inclusão de pessoas com deficiência

### Pontuais
- id 92 — teoria/análise: empréstimo modal no pop rock dos anos 1980
- id 109 — música indígena/etnomusicologia (transversal ao Eixo 2)

## 3. Leitura

O curso de Música aparece **fortemente territorializado**: mesmo os trabalhos
"pedagógicos" mobilizam repertório e contextos locais — festivais, gêneros do
Norte, igrejas e terreiros de Boa Vista, musicalidades indígenas. O foco
predominante é **formar o professor de música para a escola básica**, com forte
presença do estágio e da Residência Pedagógica; em paralelo, há uma veia
consistente de **música e cultura regional** e nichos emergentes (inclusão,
ritual religioso, música indígena).

## 4. Limites

- N = 21: estatística instável; os eixos são **indício a confirmar por leitura**.
- Os eixos **se sobrepõem** (ex.: id 95, 83 e 109 pertencem a mais de um).
- A análise reflete **a coleta atual** (cadastro NECPF), não o universo de TCCs
  de Música do curso — ausências são lacuna de coleta, não inexistência.

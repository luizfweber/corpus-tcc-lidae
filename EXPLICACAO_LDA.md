# Como o LIDAE descobre os "assuntos" dos TCCs: a técnica LDA

**Observatório Roraimense da Formação Docente — LIDAE/NECPF–UFRR**

## A pergunta de partida

Temos mais de uma centena de trabalhos de conclusão de curso (TCCs) das licenciaturas da UFRR. Lê-los um a um, classificando seus temas à mão, seria lento e sujeito ao olhar de quem classifica. Existe uma forma de o computador sugerir, sozinho, sobre quais assuntos esses trabalhos falam? Existe — e uma das técnicas mais usadas para isso chama-se **LDA**.

## A ideia, em uma frase

A LDA parte de uma suposição simples e intuitiva: **todo texto fala de mais de um assunto ao mesmo tempo, em proporções diferentes**. Um TCC pode ser, digamos, 70% sobre cultura e saberes tradicionais e 30% sobre material didático; outro pode misturar esses mesmos temas em proporção inversa.

A partir das palavras que efetivamente aparecem nos trabalhos, o algoritmo faz duas coisas ao mesmo tempo:

- Agrupa palavras que costumam aparecer juntas, formando **temas** (por exemplo, um conjunto onde *língua, cultura, comunidade e escola* têm peso alto).
- Estima a **proporção de cada tema** dentro de cada TCC.

É como observar muitas receitas sem conhecer os pratos e, só pelos ingredientes que se repetem, deduzir que existem "receitas de bolo", "de sopa" e "de salada" — e depois dizer quanto de cada estilo há em cada prato.

## Um cuidado essencial

O computador entrega **listas de palavras**, não rótulos prontos. Quem dá o nome "cultura e interculturalidade" a um conjunto de palavras é o pesquisador, depois de olhar o resultado. Mais importante: a técnica identifica **quais palavras aparecem com frequência**, e não necessariamente qual é o foco central do trabalho. Um TCC pode citar "indígena" de passagem sem que esse seja seu tema principal.

Por isso, no LIDAE, o resultado da LDA é tratado como **indício, um ponto de partida para a leitura** — nunca como conclusão definitiva. A interpretação final exige a leitura cuidadosa dos textos pelos pesquisadores.

## Em resumo

A LDA não substitui o olhar humano: ela organiza o material e aponta padrões que mereceriam, de outro modo, semanas de leitura manual. O computador sugere os caminhos; a interpretação continua sendo nossa.

---

*Métodos computacionais como instrumentos de leitura, não como veredito.*

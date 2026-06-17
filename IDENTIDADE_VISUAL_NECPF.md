# Identidade Visual — NECPF
**Sistema de design para o dashboard de dados de pesquisa**
*Núcleo de Estudos em Educação, Cultura, Poder e Formação · CCLA / UFRR*

> Documento de referência derivado da **logo do NECPF** (livro aberto + folhas amazônicas + rio). Define cores, escalas, tokens, tipografia e regras de uso para a construção de interfaces e dashboards de dados com identidade consistente.

---

## 1. Conceito da marca

A logo do NECPF reúne quatro elementos que orientam toda a identidade:

| Elemento | Significado | Cor associada |
|---|---|---|
| **Livro aberto** | Conhecimento, formação, produção acadêmica | Capa em azul-teal · páginas em verde |
| **Folhas amazônicas** | Território, contexto roraimense/amazônico | Verde-floresta + âmbar |
| **Rio (linhas sinuosas)** | Rio Branco; fluxo, percurso formativo | Branco sobre verde |
| **Logotipo "NECPF"** | Assinatura institucional | Verde-floresta |

**Princípio de aplicação:** o verde-floresta é a cor institucional dominante (estrutura, texto, identidade); azul-teal, âmbar e terracota são cores de apoio e de dados, usadas para categorizar, destacar e diferenciar — nunca competindo com o verde como base.

---

## 2. Cores da marca (âncoras)

| Nome | Hex | Papel principal |
|---|---|---|
| **Verde-floresta** | `#1B5E3B` | Cor institucional, texto de destaque, cabeçalhos, estrutura |
| **Azul-teal** | `#1A7A8A` | Cor de apoio primária, links, elementos interativos |
| **Âmbar** | `#D4A017` | Destaque, atenção, dados em evidência |
| **Terracota** | `#C1440E` | Alerta, ênfase pontual, contraste quente |

---

## 3. Escalas de cor (tints e shades para UI)

Cada cor-âncora expandida em escala 50–900 para uso em fundos, bordas, estados (hover/active), preenchimentos de gráfico e texto sobre fundos claros/escuros.

### Verde-floresta — `--verde`

| Token | Hex | Uso sugerido |
|---|---|---|
| verde-50 | `#E8F1EC` | Fundo de seção, faixa sutil |
| verde-100 | `#C6DDD0` | Fundo de card, hover claro |
| verde-200 | `#9FC6AE` | Borda suave, divisórias |
| verde-300 | `#6FA888` | Ícones secundários |
| verde-400 | `#468A66` | Estado hover de botão |
| verde-500 | `#2A724A` | — |
| **verde-600** | **`#1B5E3B`** | **Base institucional** |
| verde-700 | `#164E31` | Texto sobre fundo claro, active |
| verde-800 | `#103A25` | Cabeçalho escuro |
| verde-900 | `#0A2718` | Fundo escuro / dark mode |

### Azul-teal — `--teal`

| Token | Hex | Uso sugerido |
|---|---|---|
| teal-50 | `#E6F2F4` | Fundo informativo |
| teal-100 | `#C2DFE4` | Hover claro |
| teal-200 | `#93C6CE` | Borda |
| teal-300 | `#5FA9B5` | Ícone secundário |
| teal-400 | `#348F9D` | Hover de link |
| **teal-500** | **`#1A7A8A`** | **Base de apoio / links** |
| teal-600 | `#156675` | Active |
| teal-700 | `#114E5A` | Texto sobre claro |
| teal-800 | `#0C3941` | — |
| teal-900 | `#07252A` | Fundo escuro |

### Âmbar — `--ambar`

| Token | Hex | Uso sugerido |
|---|---|---|
| ambar-50 | `#FBF4E1` | Fundo de destaque suave |
| ambar-100 | `#F6E5B3` | Realce de fundo |
| ambar-200 | `#EFD174` | Borda de destaque |
| ambar-300 | `#E6BC3E` | — |
| ambar-400 | `#DCAD24` | Hover |
| **ambar-500** | **`#D4A017`** | **Base de destaque** |
| ambar-600 | `#B08412` | Active |
| ambar-700 | `#88660E` | Texto âmbar sobre claro |
| ambar-800 | `#5F480A` | — |
| ambar-900 | `#3A2C06` | — |

### Terracota — `--terracota`

| Token | Hex | Uso sugerido |
|---|---|---|
| terracota-50 | `#FBEAE3` | Fundo de alerta suave |
| terracota-100 | `#F4C9B6` | Realce |
| terracota-200 | `#EBA384` | Borda de alerta |
| terracota-300 | `#DF7B53` | — |
| terracota-400 | `#D45D2E` | Hover |
| **terracota-500** | **`#C1440E`** | **Base de alerta/ênfase** |
| terracota-600 | `#A23A0C` | Active |
| terracota-700 | `#7C2C09` | Texto sobre claro |
| terracota-800 | `#561F06` | — |
| terracota-900 | `#331303` | — |

### Neutros (cinza com leve calor)

| Token | Hex | Uso |
|---|---|---|
| neutro-0 | `#FFFFFF` | Fundo de card / superfície |
| neutro-50 | `#F7F8F6` | Fundo de página (light) |
| neutro-100 | `#EEF0EC` | Fundo secundário |
| neutro-200 | `#DEE1DB` | Bordas, divisórias |
| neutro-300 | `#C2C7BE` | Bordas de input |
| neutro-400 | `#9AA096` | Texto desabilitado, placeholder |
| neutro-500 | `#6E746A` | Texto secundário |
| neutro-600 | `#4E534A` | Texto de apoio |
| neutro-700 | `#363A33` | Texto de corpo |
| neutro-800 | `#23261F` | Texto principal |
| neutro-900 | `#14160F` | Fundo de página (dark) |

---

## 4. Cores semânticas (estados do dashboard)

A paleta mapeia de forma natural para os estados de interface:

| Estado | Cor base | Token sugerido | Fundo claro | Texto |
|---|---|---|---|---|
| **Sucesso / positivo** | Verde-floresta | `verde-600` | `verde-50` | `verde-700` |
| **Informação / neutro** | Azul-teal | `teal-500` | `teal-50` | `teal-700` |
| **Atenção / aviso** | Âmbar | `ambar-500` | `ambar-50` | `ambar-700` |
| **Erro / crítico** | Terracota | `terracota-500` | `terracota-50` | `terracota-700` |

---

## 5. Paleta de visualização de dados

### 5.1 Categórica (séries qualitativas)

Ordem recomendada para máxima distinção entre categorias:

| Ordem | Cor | Hex |
|---|---|---|
| 1 | Verde-floresta | `#1B5E3B` |
| 2 | Azul-teal | `#1A7A8A` |
| 3 | Âmbar | `#D4A017` |
| 4 | Terracota | `#C1440E` |
| 5 | Verde médio | `#468A66` |
| 6 | Teal claro | `#5FA9B5` |
| 7 | Âmbar profundo | `#88660E` |
| 8 | Terracota clara | `#DF7B53` |

> Para **3 ou menos categorias**, use as cores 1–3. Para gráficos de barra com uma série única, prefira `teal-500` ou `verde-600` sólido, reservando âmbar/terracota para realçar valores específicos.

### 5.2 Sequencial (intensidade / volume)

Útil para mapas de calor, contagens (ex.: TCCs por ano, por curso):

`#E8F1EC → #9FC6AE → #468A66 → #1B5E3B → #103A25`

### 5.3 Divergente (desvio em relação a um ponto médio)

Útil para comparações acima/abaixo de uma referência:

`#7C2C09 → #D45D2E → #FBEAE3 → #93C6CE → #114E5A`
*(terracota = polo negativo · neutro claro = centro · teal = polo positivo)*

---

## 6. Tipografia

| Função | Fonte recomendada | Peso | Observação |
|---|---|---|---|
| **Títulos / cabeçalhos** | Montserrat | 600–700 | Coerente com a identidade dos materiais do NECPF |
| **Corpo / interface** | Inter (ou Open Sans) | 400–500 | Alta legibilidade em telas e tabelas |
| **Números / dados** | Inter *tabular* ou JetBrains Mono | 400–600 | Use *tabular figures* (`font-variant-numeric: tabular-nums`) para alinhar colunas numéricas |

**Escala tipográfica sugerida (dashboard):**

| Token | Tamanho | Uso |
|---|---|---|
| display | 32–40px | Título principal do dashboard |
| h1 | 28px | Título de página |
| h2 | 22px | Título de seção / card grande |
| h3 | 18px | Título de card |
| body | 15–16px | Texto padrão |
| small | 13px | Legendas, rótulos de eixo |
| caption | 11–12px | Notas, metadados |

---

## 7. Variáveis CSS (pronto para uso)

```css
:root {
  /* === Cores-âncora === */
  --verde:      #1B5E3B;
  --teal:       #1A7A8A;
  --ambar:      #D4A017;
  --terracota:  #C1440E;

  /* === Verde-floresta === */
  --verde-50:  #E8F1EC; --verde-100: #C6DDD0; --verde-200: #9FC6AE;
  --verde-300: #6FA888; --verde-400: #468A66; --verde-500: #2A724A;
  --verde-600: #1B5E3B; --verde-700: #164E31; --verde-800: #103A25;
  --verde-900: #0A2718;

  /* === Azul-teal === */
  --teal-50:  #E6F2F4; --teal-100: #C2DFE4; --teal-200: #93C6CE;
  --teal-300: #5FA9B5; --teal-400: #348F9D; --teal-500: #1A7A8A;
  --teal-600: #156675; --teal-700: #114E5A; --teal-800: #0C3941;
  --teal-900: #07252A;

  /* === Âmbar === */
  --ambar-50:  #FBF4E1; --ambar-100: #F6E5B3; --ambar-200: #EFD174;
  --ambar-300: #E6BC3E; --ambar-400: #DCAD24; --ambar-500: #D4A017;
  --ambar-600: #B08412; --ambar-700: #88660E; --ambar-800: #5F480A;
  --ambar-900: #3A2C06;

  /* === Terracota === */
  --terracota-50:  #FBEAE3; --terracota-100: #F4C9B6; --terracota-200: #EBA384;
  --terracota-300: #DF7B53; --terracota-400: #D45D2E; --terracota-500: #C1440E;
  --terracota-600: #A23A0C; --terracota-700: #7C2C09; --terracota-800: #561F06;
  --terracota-900: #331303;

  /* === Neutros === */
  --neutro-0:   #FFFFFF; --neutro-50:  #F7F8F6; --neutro-100: #EEF0EC;
  --neutro-200: #DEE1DB; --neutro-300: #C2C7BE; --neutro-400: #9AA096;
  --neutro-500: #6E746A; --neutro-600: #4E534A; --neutro-700: #363A33;
  --neutro-800: #23261F; --neutro-900: #14160F;

  /* === Semânticas === */
  --sucesso:   var(--verde-600);
  --info:      var(--teal-500);
  --aviso:     var(--ambar-500);
  --erro:      var(--terracota-500);

  /* === Superfícies (light) === */
  --bg-pagina:    var(--neutro-50);
  --bg-superficie: var(--neutro-0);
  --borda:        var(--neutro-200);
  --texto:        var(--neutro-800);
  --texto-fraco:  var(--neutro-500);
  --marca:        var(--verde-600);
  --link:         var(--teal-500);

  /* === Tipografia === */
  --fonte-titulo: "Montserrat", system-ui, sans-serif;
  --fonte-corpo:  "Inter", "Open Sans", system-ui, sans-serif;
  --fonte-dados:  "Inter", "JetBrains Mono", monospace;
}

/* Paleta categórica para gráficos */
:root {
  --viz-1: #1B5E3B; --viz-2: #1A7A8A; --viz-3: #D4A017; --viz-4: #C1440E;
  --viz-5: #468A66; --viz-6: #5FA9B5; --viz-7: #88660E; --viz-8: #DF7B53;
}
```

---

## 8. Uso da logo

- **Marca d'água em cards de dados:** logo do NECPF em branco, canto inferior, 20–30% de opacidade.
- **Cabeçalho do dashboard:** logo em versão completa sobre fundo claro (`neutro-0` ou `neutro-50`), ou versão branca sobre faixa `verde-600`/`verde-800`.
- **Área de proteção:** manter ao redor da logo um espaço livre equivalente à altura da letra "N" do logotipo.
- **Não fazer:** alterar as cores da logo, aplicar sobre fundos de baixo contraste, distorcer proporções ou rotacionar.

---

## 9. Recomendações de acessibilidade

- Texto de corpo sobre fundo claro: use `neutro-700`/`neutro-800` (contraste AA).
- Verde-floresta (`verde-600`) como texto sobre branco atinge contraste AA para títulos e textos grandes; para corpo pequeno, prefira `verde-700`.
- Âmbar (`ambar-500`) tem contraste baixo sobre branco para texto — use-o em **preenchimentos e destaques**, não em texto pequeno; para rótulos, use `ambar-700`.
- Não codifique informação **apenas** por cor em gráficos: combine com rótulos, padrões ou ícones (importante para séries de dados de pesquisa).

---

*Identidade derivada da logo do NECPF e da paleta consolidada do projeto. Pronta para alimentar tokens de design, folhas de estilo e bibliotecas de gráficos do dashboard de dados de pesquisa.*

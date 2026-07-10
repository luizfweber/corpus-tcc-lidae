# Cobertura da coleta por curso (LIDAE/NECPF) — janela 2015–2025

> **Cobertura = TCCs coletados na janela ÷ egressos da janela** (CLAUDE.md §5).
> Exploratório, não censitário: o corpus é um piloto desbalanceado (§1).
> Atualizado em 10/07/2026, após a chegada da base individual de egressos da DTI.

## Como cada número foi obtido

- **Numerador (TCCs):** contagem no corpus (`corpus_tccs_consolidado.csv`, 321
  TCCs) por `grupo_tcc`, restrita a defesas com `ano_defesa` entre 2015 e 2025
  (281 dos 321). Anos ausentes/implausíveis ficam de fora, não são imputados (§2).
- **Denominador A (DTI):** base individual `egressos_dti_licenciaturas_2026-07-10.csv`,
  contando **egressos distintos** (matrícula única) cujo `afastamento_permanente`
  cai entre 2015 e 2025. Excluídos: bacharelado explícito `(B)`; sentinela 2099;
  vazios.
- **Denominador B (série histórica):** `egressos_serie_historica.csv` (canônico,
  reconciliado com a PROEG e **estendido até 2025.2 com o incremento da DTI** —
  ver período 6, coluna `fonte`), janela = acumulado 2025.2 menos acumulado
  2009–2014.2.

## Resultado

| grupo_tcc | TCC total | TCC 15–25 | egr DTI | egr hist | cob DTI % | cob hist % |
|---|--:|--:|--:|--:|--:|--:|
| História | 122 | 96 | 171 | 168 | **56,1** | 57,1 |
| Música | 22 | 22 | 46 | 46 | **47,8** | 47,8 |
| Matemática | 15 | 14 | 56 | 53 | 25,0 | 26,4 |
| Insikiran | 87 | 87 | 353 | 371 | 24,6 | 23,5 |
| Pedagogia | 29 | 27 | 202 | 205 | 13,4 | 13,2 |
| LEDUCARR | 16 | 15 | 122 | 126 | 12,3 | 11,9 |
| Ciências Biológicas | 20 | 10 | 107 | 74 | 9,3 | 13,5 |
| Letras | 10 | 10 | 152 | 158 | 6,6 | 6,3 |
| Artes Visuais | 0 | 0 | 73 | 75 | 0,0 | 0,0 |
| Física | 0 | 0 | 29 | 28 | 0,0 | 0,0 |
| Geografia | 0 | 0 | 136 | 116 | 0,0 | 0,0 |
| Química | 0 | 0 | 62 | 64 | 0,0 | 0,0 |

**Global na janela:** 281 TCCs ÷ ~1.509 egressos (DTI) ≈ **18,6%**. Com a série
estendida a 2025.2, as duas fontes ficam próximas (ex.: Música 46 = 46).

## Leitura (indício, não veredito — §4)

- A coleta é mais **profunda** em História (56%) e Música (48%): onde o NECPF
  concentrou esforço. Insikiran tem a maior massa absoluta (87 TCCs).
- **Quatro cursos com cobertura zero na janela** (Geografia, Química, Física,
  Artes Visuais) são a maior lacuna a preencher. Ciências Biológicas saiu do zero
  (agora 20 TCCs) mas ainda é baixa.
- Não confundir cobertura baixa com "pouca produção": é **disponibilidade de
  acervo coletado**, não medida de produção docente (§4, §6).

## Ressalvas da fonte (preservadas, não corrigidas — §3)

1. **Conceito do denominador DTI:** `afastamento_permanente` é a **saída/colação
   de grau**, não a data de defesa. É "quem se formou na janela", aproximação
   legítima do universo de egressos, mas evento distinto da defesa do TCC.
2. **Licenciatura × bacharelado:** só Ciências Biológicas mistura as duas
   modalidades na DTI. Excluímos o `(B)` explícito, mas restam 114 registros de
   habilitação vazia (ambíguos) — por isso a série histórica (que isola "(L)")
   é o denominador **mais confiável** para Cs. Biológicas (63, não 107).
3. **Discrepância DTI × série histórica:** as duas fontes concordam de perto em
   quase todos os cursos; divergem em Cs. Biológicas (ver acima) e Geografia
   (136 vs 102). Mantidas as duas colunas; o número oficial deve ser confirmado
   com a PROEG antes de publicação.
4. O corpus cresce; estes percentuais são um retrato de 10/07/2026.

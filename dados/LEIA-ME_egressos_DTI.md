# Registro: base de egressos UFRR (DTI, 10/07/2026)

## Identificação da fonte

- **Arquivo:** `egressos_dti_2026-07-10.csv` (nesta pasta; cópia do original em
  `[Projeto de pesquisa] UFRR - TCCs/Dados da pesquisa inicial - PROEG/`)
- **Origem:** DTI/UFRR, atendendo solicitação da pesquisa LIDAE/NECPF
- **Data de recebimento:** 10/07/2026
- **Abrangência:** todos os cursos de graduação da UFRR (48 cursos), não apenas
  as licenciaturas

## ⚠️ Dados pessoais (LGPD)

O arquivo contém **nome completo e matrícula** de estudantes. Por isso ele está
no `.gitignore` e **não pode ser versionado no repositório público** nem usado
diretamente no dashboard sem agregação/anonimização. Apenas este Leia-me (sem
dados pessoais) é versionado.

## Estrutura (9 colunas)

| Coluna | Conteúdo |
|---|---|
| `#` | número sequencial da linha |
| `curso_nome` | curso (48 valores; ver observações) |
| `curso_habilitacao` | habilitação, quando houver (ex.: `INGLÊS v. I`, `INTERCULTURAL INDÍGENA - HAB. CIÊNCIAS DA NATUREZA`, `QUÍMICA v. II`); `v. I/II/III` parecem indicar versões de currículo |
| `pessoa_nome` | nome completo do egresso (dado pessoal) |
| `discente_matricula` | matrícula (dado pessoal; chave para deduplicar) |
| `titulo` | título do TCC, quando registrado no sistema |
| `orientador` | orientador do TCC, quando registrado |
| `afastamento_permanente` | período de saída definitiva (formato `AAAA.S`) |
| `matriculas_validas` | conjunto de períodos com matrícula ativa (formato `{2024.2,2024.1,...}`) |

## Números gerais (como foram obtidos: contagem direta no CSV, sem filtro)

- **15.428 linhas** | **14.244 matrículas distintas** | 13.933 nomes distintos
  (linhas > matrículas porque há estudantes com **2 registros de TCC**; 116
  casos nas licenciaturas)
- **Com título de TCC:** 6.304 linhas | com orientador: 6.285
- **Período de saída:** 1984 a 2099 (ver artefatos) | 670 linhas sem valor
- **Licenciaturas do corpus TCC:** 5.587 linhas | 5.465 matrículas distintas |
  1.166 com título de TCC (21%)

## Artefatos e pendências da fonte (preservar, não corrigir em silêncio)

1. **`afastamento_permanente = 2099`** em alguns registros: valor sentinela do
   sistema, não é ano real. Tratar como ausente na análise, preservar no dado.
2. **670 linhas sem `afastamento_permanente`**: não imputar; excluir das
   estatísticas por ano (CLAUDE.md §2).
3. **A definição de "egresso" usada pela DTI não veio explicitada.** Não se sabe
   ainda se a extração inclui apenas formados (colação de grau) ou também outras
   formas de saída. **Confirmar com a DTI/PROGRAD antes de usar como denominador
   de cobertura.**
4. **Duplicidade por matrícula** (mesma pessoa com 2 títulos de TCC): decidir
   regra de contagem — egresso conta 1 vez; TCC pode contar 2.
5. **Granularidade de curso difere da série histórica PROEG** (`egressos_serie_historica.csv`):
   ex. aqui `LICENCIATURA INTERCULTURAL` aparece como curso + 3 habilitações e
   também como 3 cursos separados; Letras tem habilitações com sufixo `v. I/II`.
   Será preciso um **de/para** novo (análogo ao `de_para_cursos_proeg.csv`).
6. **Reconciliação com a série histórica (4.544) ainda não feita** — os totais
   desta base individual devem ser confrontados com os acumulados da PROEG antes
   de substituir qualquer número canônico (CLAUDE.md §5, §6).

## Valor para a pesquisa

- Base **individual** (um egresso por linha): permite recompor qualquer janela
  temporal sem depender de acumulados.
- `titulo` + `orientador` permitem **casar egresso ↔ TCC coletado** (validação
  da coleta NECPF e detecção de TCCs existentes ainda não coletados).
- `curso_habilitacao` destrava a cobertura **por habilitação** (Letras,
  Insikiran, LEDUCARR, Química).

## Próximos passos (combinados em 10/07/2026)

- [ ] Ajustar/normalizar os dados com o pesquisador (nomes de curso, de/para)
- [ ] Confirmar com DTI/PROGRAD a definição de egresso da extração
- [ ] Reconciliar totais com `egressos_serie_historica.csv`
- [ ] Gerar agregados anonimizados (por curso × ano) para uso no dashboard

# Mapa do fluxo de dados (corpus_v2) — LIDAE/NECPF

Onde cada arquivo vive, quem o gera e quem o lê. Regra de ouro: **fonte** é
editável e versionada; **derivado** nunca é editado à mão, sempre regenerado.

## Camadas

```
dados/
  _pessoais/    FONTE SENSÍVEL (LGPD)  -> pasta inteira gitignorada, nunca publicar
  canonico/     FONTE canônica         -> editável à mão, versionada
outputs/        DERIVADO               -> gerado por script, reproduzível
outputs/backups/  snapshots de rollback (retenção: ~5 mais recentes)
```

Não há pasta `derivado/` dentro de `dados/`: **o derivado é a `outputs/`**.
Nada em `dados/` é gerado por script; tudo ali é fonte.

## dados/_pessoais/ (sensível, fora do git)

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `egressos_dti_2026-07-10.csv` | base completa DTI (48 cursos, nome+matrícula) | DTI/UFRR |
| `egressos_dti_licenciaturas_2026-07-10.csv` | recorte das licenciaturas + grupo_tcc | filtro da anterior |
| `matriculas_por_id.csv` | de-para id do TCC -> matrícula (145) | cruzamento corpus × DTI |
| `CONFERENCIA_DTI_2026-07-10.csv` | listas de conferência (matrícula/orientador/autor) | cruzamento corpus × DTI |

## dados/canonico/ (fonte, versionada)

| Arquivo | Conteúdo | Quem lê |
|---|---|---|
| `egressos_serie_historica.csv` | egressos acumulados por período e curso; col. `fonte` (PROEG / DTI 2025.2) | `dashboard.py`, cálculo de cobertura |
| `de_para_cursos_proeg.csv` | mapa nome PROEG -> curso_det -> grupo_tcc (escopo do estudo) | referência de normalização |
| `egressos_por_curso.csv` | total de egressos por curso | `dashboard.py` |
| `egressos_por_ano.csv` | egressos por curso e ano | `dashboard.py` |
| `egressos_publico.csv` | egressos individuais SEM matrícula (nome, curso, período, título), 1 por pessoa | `dashboard.py` (aba Registros faltantes) |

`egressos_publico.csv` é **gerado** por `gerar_egressos_publico.py` a partir da
base sensível em `_pessoais/`. Proteção parcial (decisão do responsável,
10/07/2026): nome/curso/período/título são públicos; **matrícula e histórico de
matrículas NÃO entram**. Deduplica por matrícula (quem tem 2 títulos conta como
1 egresso). Rode o gerador de novo quando chegar base nova da DTI.

## Corpus de TCCs (fonte + derivado)

| Arquivo | Camada | Quem gera | Quem lê |
|---|---|---|---|
| `outputs/corpus_tccs_consolidado.csv` | fonte (montada) | `importar_catalogacao.py` | `analise_corpus.py` |
| `outputs/analise/corpus_tccs_analisado.csv` | DERIVADO | `analise_corpus.py` | `dashboard.py`, `analise_por_curso.py` |
| `outputs/analise/cobertura_por_curso.csv` | DERIVADO | cálculo de cobertura | relatório |
| `outputs/analise/*.png`, `*.md`, `*.txt` | DERIVADO | pipeline | relatórios |

## Pipeline vivo (ordem de execução)

```
nova catalogação (CSV do formulário)
        │  importar_catalogacao.py   (limpa nomes/banca, dedup, anexa)
        ▼
outputs/corpus_tccs_consolidado.csv
        │  analise_corpus.py          (tópicos LDA, clusters, indígena; descarta matricula)
        ▼
outputs/analise/corpus_tccs_analisado.csv ──> dashboard.py (Streamlit / nuvem)
        │  analise_por_curso.py       (sub-temas por curso)
        ▼
outputs/analise/analise_por_curso.{md,json}
```

QA: `verifica_inconsistencias.py`. Scripts one-off já cumpridos: `scripts/legado/`.

## LGPD em uma linha

Dado pessoal (nome, matrícula) só em `dados/_pessoais/` (gitignorado). O
consolidado e o analisado são limpos; `analise_corpus.py` tem filtro que
descarta `matricula` caso ela reapareça por engano. Nada com dado pessoal vai
para o GitHub nem para o dashboard.

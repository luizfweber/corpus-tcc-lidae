# Scripts legados (uso pontual, já cumprido)

Scripts de tarefas únicas que já foram executadas e **não fazem parte do
pipeline vivo**. Guardados para referência/reprodutibilidade histórica.
Não rode como rotina.

- `integra_novos_tccs.py` — integração antiga de novos TCCs (hoje: `importar_catalogacao.py`)
- `reimporta_tipo_tcc.py` — reimportação pontual do campo tipo_tcc
- `inspeciona_topicos_k4.py` — inspeção exploratória de tópicos com K=4
- `estabilidade_lda.py` — teste de estabilidade do LDA (uma vez)

Pipeline vivo (na raiz de `corpus_v2/`): `importar_catalogacao.py` →
`analise_corpus.py` → `analise_por_curso.py` → `dashboard.py`. Utilitário de
QA: `verifica_inconsistencias.py`.

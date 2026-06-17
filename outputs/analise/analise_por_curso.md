# Análise temática por curso, em camadas — LIDAE/UFRR

Corpus: 145 TCCs. Tratamento conforme o N de cada curso (LDA · descritivo · listagem). Exploratório, não censitário.


## 🟢 Camada LDA (N suficiente para sub-temas)

### Insikiran — 72 TCCs · LDA intra-curso (K=2)
*Seleção de K por estabilidade entre 8 seeds — K2: ARI=0.21 · K3: ARI=0.17 · K4: ARI=0.16. Escolhido K=2 (ARI=0.21).*
> ⚠️ Estabilidade baixa (ARI=0.21): sub-temas FRÁGEIS, indício a confirmar por leitura — não conclusão.

**Sub-tema 1** (50 TCCs) — educacao, indigenas, estadual, escolar, conhecimentos, cultura, matematica, proposta, atividades, pedagogica
   - id 140 (2021): O USO DOS ALIMENTOS INDÍGENAS WAPICHANA COMO PRÁTICA PEDAGÓGICA EDUCATIVA NA COMUNIDADE IN
   - id 71 (2022): PROPOSTA PEDAGÓGICA COLHER MILHO NA ROÇA: atividade social indígena como proposta de inter
   - id 27 (2024): CONSTRUINDO UMA PROPOSTA PEDAGÓGICAS A PARTIR DA ATIVIDADE SOCIAL “CULTIVAR MANIVAS (Manih

**Sub-tema 2** (22 TCCs) — leitura, lingua, jogos, plantas, projeto, conhecimento, escrita, medicinais, material, estadual
   - id 11 (2024): RELATO DE EXPERIÊNCIA: LEITURA E PRODUÇÃO DE JOGOS PEDAGÓGICOS NO ENSINO FUNDAMENTAL I NA 
   - id 61 (2024): RELATO DE EXPERIÊNCIA NA ESCOLA ESTADUAL INDÍGENA TUXAUA EVARISTO:SOLETRANDO NA ESCOLA
   - id 54 (2024): ESTRATÉGIAS DE LEITURA E ESCRITA DOS ALUNOS DO 50 ANO DO ENSINO FUNDAMENTAL I DA ESCOLA ES


### Pedagogia — 28 TCCs · LDA intra-curso (K=3)
*Seleção de K por estabilidade entre 8 seeds — K2: ARI=0.12 · K3: ARI=0.18. Escolhido K=3 (ARI=0.18).*
> ⚠️ Estabilidade baixa (ARI=0.18): sub-temas FRÁGEIS, indício a confirmar por leitura — não conclusão.

**Sub-tema 1** (13 TCCs) — educacao, pedagogica, coordenacao, especial, pedagogico, vista, pandemia, covid, municipal, programa
   - id 31 (0000): DESAFIOS E POSSIBILIDADES DA COORDENAÇÃO PEDAGÓGICA EM RORAIMA: UM OLHAR A PARTIR DOS TRAB
   - id 22 (2023): RELAÇÃO PÚBLICO-PRIVADO: INSTITUTO ALFA E BETO E SUA PROPOSTA DE EDUCAÇÃO NA REDE PÚBLICA 
   - id 36 (2019): ATRIBUIÇÕES DO COORDENADOR PEDAGÓGICO NAS ESCOLAS MUNICIPAIS DE BOA VISTA-RR: UMA ANÁLISE 

**Sub-tema 2** (7 TCCs) — educacao, hospitalar, pedagogia, crianca, educacional, autismo, atividades, pedagogo, tambem, infantil
   - id 112 (2019): PEDAGOGIA HOSPITALAR: CLASSE HOSPITALAR NAS UNIDADES PÚBLICAS DE SAÚDE DE ALTA COMPLEXIDAD
   - id 113 (2019): PERFIL DOS ESTAGIÁRIOS DO CURSO DE PEDAGOGIA DA UFRR QUE ACOMPANHAM ALUNOS COM AUTISMO EM 
   - id 32 (2018): JOGOS E BRINCADEIRAS NO PROCESSO DE APRENDIZAGEM NA PRÉ-ESCOLA

**Sub-tema 3** (8 TCCs) — estagio, formacao, pedagogia, supervisionado, experiencia, experiencias, curricular, ufrr, diversidade, processo
   - id 47 (Não informado): O ESTÁGIO CURRICULAR COMO MOMENTO DE APRENDIZAGEM SOBRE A ATUAÇÃO DO PEDAGOGO EM CONTEXTO 
   - id 45 (2018): UMA EXPERIÊNCIA DE CONTAÇÃO DE HISTÓRIAS NO ESTÁGIO CURRICULAR SUPERVISIONADO COM FOCO NA 
   - id 34 (2022): REFLEXÕES SOBRE AS EXPERIÊNCIAS NO ESTÁGIO CURRICULAR DO CURSO DE PEDAGOGIA NAS MODALIDADE



## 🟠 Camada descritiva (N médio — termos + leitura)

### Música — 19 TCCs · descritivo (sem LDA)
*N insuficiente para modelagem de tópicos; reporta-se a frequência documental dos termos e a lista de trabalhos.*

**Termos mais recorrentes (nº de TCCs):** musica (17), musical (13), analise (12), vista (12), educacao (12), pratica (11), roraima (10), contexto (10), dados (9), musicais (9), praticas (9), resultados (9), alem (8), bibliografica (8), atraves (8)

**Trabalhos:**
   - id 92 (2017): O EMPRÉSTIMO MODAL RECORRENTE NO POP ROCK DOS ANOS 1980
   - id 84 (2019): FESTIVAL FOLCLÓRICO DE CARACARAÍ
   - id 89 (2019): AULAS DE PIANO EM GRUPO NO MÉTODO SUZUKI: UMA ANÁLISE NO ESTÚDIO SUZUKI DE EDUCAÇÃO MUSICA
   - id 91 (2019): "IMPORTA SIM QUE PENSEMOS JUNTOS SOBRE EDUCAÇÃO MUSICAL”: REFLEXÕES SOBRE AULAS DE MÚSICA 
   - id 93 (2019): A PRODUÇÃO CIENTÍFICA DE EDUCAÇÃO MUSICAL SOB O ENFOQUE DAS POLÍTICAS PÚBLICAS DE INCLUSÃO
   - id 94 (2019): Práticas de canto no Curso de Licenciatura em Música da UFRR: impactos na atuação do licen
   - id 98 (2019): A IMPORTÂNCIA DA REGÊNCIA NAS AULAS DE MÚSICA NA EDUCAÇÃO BÁSICA
   - id 108 (2019): A COLABORAÇÃO PIANÍSTICA NO CORO DA IGREJA BATISTA REGULAR DE BOA VISTA: COMPETÊNCIAS EXER
   - id 83 (2020): CONTRABAIXO ELÉTRICO: UM ESTUDO DAS LEVADAS EM QUATRO GÊNEROS MUSICAIS DA REGIÃO NORTE
   - id 85 (2021): PRÁTICAS INFORMAIS DE APRENDIZAGEM MUSICAL NA FORMAÇÃO DISCENTE DO CURSO DE LICENCIATURA E
   - id 87 (2021): MÚSICA E MOVIMENTO: "O PASSO" COMO POSSIBILIDADE INTERDISCIPLINAR ENTRE MÚSICA E EDUCAÇÃO 
   - id 95 (2021): MÚSICAS REGIONALISTAS DO FESTIVAL CANTO FORTE: ATIVIDADES PARA O ENSINO DE MÚSICA NA EDUCA
   - id 97 (2021): FESTIVAL FOLCLÓRICO DE CARACARAÍ: A PERCUSSÃO NOS GRUPOS COBRA MARIANA E GAVIÃO CARACARÁ
   - id 109 (2022): MÚSICA INDÍGENA PARA FLAUTA DOCE: POSSIBILIDADES DIDÁTICAS COM MUSICALIDADES DE QUATRO EST
   - id 90 (2024): ENSINO E APRENDIZAGEM DE MÚSICA ATRAVÉS DE PRÁTICAS DE CANTO CORAL NA IGREJA BATISTA REGUL
   - id 82 (2025): ESCOLAS DE SAMBA EM BOA VISTA (RR): UM ESTUDO A PARTIR DAS MEMÓRIAS DE PRATICANTES DE DUAS
   - id 86 (2025): PRÁTICAS DE ENSINO DE MÚSICA: EXPERIÊNCIA DE FORMAÇÃO DOCENTE NO PROGRAMA RESIDÊNCIA PEDAG
   - id 96 (2025): ENSINO COLETIVO DE VIOLÃO NA ORQUESTRA DE VIOLÕES DO INSTITUTO BOA VISTA DE MÚSICA (IBVM):
   - id 99 (2025): CONSIDERAÇÕES SOBRE A MÚSICA RITUAL NO TERREIRO DE UMBANDA OGUM MATINATA EM BOA VISTA – RR

### Matemática — 15 TCCs · descritivo (sem LDA)
*N insuficiente para modelagem de tópicos; reporta-se a frequência documental dos termos e a lista de trabalhos.*

**Termos mais recorrentes (nº de TCCs):** teoria (14), acoes (14), problema (14), atividade (14), situacoes (14), estudantes (13), galperin (13), resolucao (13), fundamental (11), matematica (11), processo (11), analisar (10), formacao (10), conteudo (10), mentais (10)

**Trabalhos:**
   - id 4 (2016): A APRENDIZAGEM DA ATIVIDADE DE SITUAÇÕES PRO-BLEMA EM SISTEMA DE EQUAÇÕES LINEARES FUNDA-M
   - id 18 (2016): Resolução de problemas como metodologia de ensino no conteúdo de estatística fundamentado 
   - id 2 (2017): Contribuições da Teoria Histórico – Cultural para uma aprendizagem desenvolvimental na res
   - id 3 (2017): RELATO DE UMA EXPERIÊNCIA DA APRENDIZAGEM NAS OPERAÇÕES MATEMÁTICAS UTILIZANDO A LINGUAGEM
   - id 1 (2018): Contribuições da teoria histórico-cultural para aprendizagem desenvolvimental em expressõe
   - id 127 (2018): UM INSTRUMENTO QUANTITATIVO DA ATIVIDADE DE SITUAÇÕES PROBLEMA EM MATEMÁTICA
   - id 128 (2018): A Atividade de Situações Problema em aprendizagem na resolução de Operações com os Números
   - id 126 (2019): DIAGNÓSTICO DO NÍVEL DE APRENDIZAGEM POR MEIO DA ATIVIDADE DE SITUAÇÕES PROBLEMA DOCENTE N
   - id 124 (2021): ATIVIDADE DE SITUAÇÕES PROBLEMA DISCENTE NA APRENDIZAGEM DE FRAÇÕES FUNDAMENTADA EM GALPER
   - id 125 (2021): ATIVIDADE DE SITUAÇÕES PROBLEMA DISCENTE NA APRENDIZAGEM NO CONCEITO DE MEDIR FUNDAMENTADO
   - id 122 (2022): ATIVIDADE DE SITUAÇÕES PROBLEMA DISCENTE NA APRENDIZAGEM DE PROPORCIONALIDADE PARA ESTUDAN
   - id 123 (2022): O PENSAMENTO ALGÉBRICO POR MEIO DA ATIVIDADE DE SITUAÇÕES PROBLEMA DISCENTE NA RESOLUÇÃO D
   - id 121 (2023): DIAGNÓSTICO DA APRENDIZAGEM EM EXPRESSÕES ALGÉBRICAS FUNDAMENTADA NA TEORIA DA ATIVIDADE E
   - id 120 (2024): A ATIVIDADE SITUAÇÕES PROBLEMA DISCENTE EM EXPRESSÕES ALGÉBRICAS EM ESTUDANTES DO 7° ANO N
   - id 119 (2026): CONTRIBUIÇÕES DA TEORIA HISTÓRICO-CULTURAL DA ATIVIDADE NA APRENDIZAGEM DA MATEMÁTICA: UM 


## 🔴 Camada listagem (N ínfimo — sem modelagem)

### Letras — 6 TCCs · listagem (sem análise)
*N ínfimo (6): qualquer modelagem seria artefato (CLAUDE.md §1). Apenas identificação.*

   - id 12 (2022): O LÉXICO RORAIMENSE NAS REDES SOCIAIS LOCAIS – KABOCANDO1
   - id 13 (2022): O QUE É UM VERBO? GRAMÁTICA, CONCORDÂNCIA VERBAL E FUNCIONALISMO LINGUÍSTICO: UM OLHAR SOBRE O ENSINO DA LÍNGU
   - id 15 (2022): TENTATIVAS DE SUICÍDIO ENTRE INGRESSOS E EGRESSOS DOS CURSOS DE LETRAS DA UNIVERSIDADE FEDERAL DE RORAIMA: FAT
   - id 16 (2022): THE CREOLE AND THE STANDARD LANGUAGE SPOKEN AT ELEMENTARY SCHOOLS IN ENGLISH GUYANA
   - id 17 (2022): THE HONEST TRUTH: TRANSLATION METHODS OVERVIEW
   - id 14 (2023): PAPÉIS SOCIAIS DE GÊNERO NO LIVRO MULHERZINHAS, DE LOUISA MAY ALCOTT

### História — 3 TCCs · listagem (sem análise)
*N ínfimo (3): qualquer modelagem seria artefato (CLAUDE.md §1). Apenas identificação.*

   - id 145 (2023): UM SONHO EM DAR RECADOS DE LONGE: A CHEGADA DA COMPANHIA TELEFÔNICA RORAIMENSE – CTR (DE 1966 A 1973)
   - id 146 (2023): OPERAÇÃO ACOLHIDA: A ESTRATÉGIA DE INTERIORIZAÇÃO E AS DIFICULDADES DE ACESSO E IMPLEMENTAÇÃO PARA OS INDÍGENA
   - id 147 (2023): O SERVIÇO NACIONAL DE INFORMAÇÕES E A ESPIONAGEM À IGREJA CATÓLICA EM RORAIMA: DA DITADURA À REDEMOCRATIZAÇÃO

### LEDUCAR — 2 TCCs · listagem (sem análise)
*N ínfimo (2): qualquer modelagem seria artefato (CLAUDE.md §1). Apenas identificação.*

   - id 19 (2023): AS CONTRIBUIÇÕES DO PROGRAMA INSTITUCIONAL DE BOLSA DE INICIAÇÃO À DOCÊNCIA-PIBID PARA A FORMAÇÃO DOCENTE DOS 
   - id 129 (2024): DA TERRA AO CONHECIMENTO: UMA PROPOSTA INTERDISCIPLINAR PARA A FORMAÇÃO CONTINUADA DE PROFESSORES DA EDUCAÇÃO 

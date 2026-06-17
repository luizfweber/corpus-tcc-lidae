# Guia de Preenchimento e Reimportação — tipo_tcc

## 1. Situação Atual

- **95 de 128 TCCs** têm a coluna `tipo_tcc` vazia
- Foram gerados dois arquivos para preenchimento:
  - `outputs/relatorio_tipo_tcc_vazio.xlsx` (recomendado — fácil de editar)
  - `outputs/relatorio_tipo_tcc_vazio.csv` (alternativa em texto)

## 2. Passo a Passo para Preenchimento

### Passo 1: Abra o relatório
Abra em Excel ou Calc:
```
corpus_v2/outputs/relatorio_tipo_tcc_vazio.xlsx
```

### Passo 2: Entenda as colunas

| Coluna | O que é | Editar? |
|---|---|---|
| id | ID único do TCC | ❌ NÃO |
| grupo_tcc | Grupo de curso | ❌ NÃO |
| titulo | Título (para identificar) | ❌ NÃO |
| autor | Autor do trabalho | ❌ NÃO |
| orientador | Orientador | ❌ NÃO |
| **pesquisador** | **QUEM CATALOGOU** ← contate | ❌ NÃO |
| ano_defesa | Ano | ❌ NÃO |
| curso_fonte | Curso original | ❌ NÃO |

### Passo 3: Preencha tipo_tcc

**Não há coluna de tipo_tcc visível no relatório!**
- Por quê? Porque ela está vazia e queremos preenchê-la
- Onde colocar? **Abra o documento original** (acesso via coluna `link`)

Para cada linha:
1. Leia o `titulo` para identificar
2. Clique no `link` (abre o TCC no Drive)
3. Abra o TCC e procure pela informação de tipo (capa, ficha catalográfica, ou pergunte ao pesquisador)
4. **Anote o tipo identificado**
5. Passe para a próxima

### Passo 4: Crie versão preenchida

Quando terminar de anotar os tipos:

**Opção A — Se preencheu em planilha separada:**
1. Crie uma nova coluna chamada `tipo_tcc` 
2. Cole os tipos que anotou
3. Salve como: `relatorio_tipo_tcc_vazio_PREENCHIDO.xlsx`

**Opção B — Se quer usar outra forma:**
- Crie um CSV com colunas `id` e `tipo_tcc`
- Salve como: `relatorio_tipo_tcc_vazio_PREENCHIDO.csv`

**Tipos aceitos pelo script:**
- Monografia ✓
- Artigo ✓
- Relato de Experiência ✓
- Trabalho de Pesquisa ✓
- Projeto ✓
- Dissertação ✓
- Tese ✓
- Estudo de Caso ✓
- Revisão Sistemática ✓
- Ensaio ✓
- Resenha ✓
- Outro ✓

## 3. Reimportação para a Base

### Passo 1: Salve o arquivo preenchido

Certifique-se de que:
- Tem coluna `id` (números: 1, 2, 3…)
- Tem coluna `tipo_tcc` (preenchida com os tipos)
- Está em `.xlsx` ou `.csv`
- Está na pasta `corpus_v2/outputs/`

### Passo 2: Execute o script de reimportação

Abra o terminal na pasta `corpus_v2` e execute:

```bash
python3 reimporta_tipo_tcc.py outputs/relatorio_tipo_tcc_vazio_PREENCHIDO.xlsx
```

Ou com CSV:
```bash
python3 reimporta_tipo_tcc.py outputs/relatorio_tipo_tcc_vazio_PREENCHIDO.csv
```

### Passo 3: Verifique o relatório

O script vai:
1. ✓ Carregar o arquivo preenchido
2. ✓ Validar os dados
3. ✓ **Criar backup** (salvo em `outputs/backups/`)
4. ✓ Atualizar a base CSV
5. ✓ Atualizar a base XLSX
6. ✓ Mostrar um relatório final

**Exemplo de saída:**
```
✓ Carregado: 95 registros
✓ Base original carregada: 128 registros
✓ Backup criado: outputs/backups/corpus_tccs_analisado_BACKUP_20260617_143022.csv
✓ Base atualizada: outputs/analise/corpus_tccs_analisado.csv
✓ Excel atualizado: outputs/analise/corpus_tccs_analisado.xlsx

RELATÓRIO DE REIMPORTAÇÃO
======================================================================
✓ Registros atualizados: 92

⚠️  Conflitos encontrados: 3
   (tipo_tcc já estava preenchido — mantido valor original)
     id 45: Artigo (novo: Monografia)
     ...

📊 Resumo final:
   Total com tipo_tcc preenchido: 123
   Distribuição:
     - Monografia: 58
     - Artigo: 35
     ...

✅ CONCLUÍDO COM SUCESSO!
```

## 4. O que o Script Faz

| Ação | Detalhe |
|---|---|
| **Valida** | Verifica se `id` e `tipo_tcc` existem e estão corretos |
| **Backup** | Salva cópia da base antes de atualizar (seguro!) |
| **Atualiza CSV** | Reimporta os tipos no arquivo `.csv` |
| **Atualiza XLSX** | Também regenera o Excel com os novos dados |
| **Detecta conflitos** | Se um TCC já tinha tipo, preserva o antigo (avisa) |
| **Relatório** | Mostra quantos foram atualizados, erros, etc. |

## 5. Segurança

- ✅ **Backup automático** — antes de qualquer mudança
- ✅ **Validação** — rejeita dados inválidos
- ✅ **Aviso de conflito** — se tipo já estava preenchido
- ✅ **Rastreabilidade** — log completo do que foi feito

## 6. Se algo der errado

**Script falhou?**
1. Verifique se o arquivo está em `outputs/`
2. Verifique se tem coluna `id` (número inteiro)
3. Verifique se tem coluna `tipo_tcc` (texto)
4. Rode novamente

**Quer desfazer?**
1. Seu backup está em `outputs/backups/`
2. Copie o backup de volta para `outputs/analise/corpus_tccs_analisado.csv`
3. Pronto — voltou ao estado anterior

## 7. Próximos Passos (após reimportação)

Quando terminar:
1. ✓ O dashboard vai refletir os novos tipos automaticamente
2. ✓ A base consolidada estará completa (100% de tipo_tcc)
3. ✓ Pode gerar novos relatórios e análises

---

**Dúvidas?** Revise as colunas no relatório ou execute:
```bash
python3 reimporta_tipo_tcc.py
```

sem argumentos para ver a mensagem de ajuda.

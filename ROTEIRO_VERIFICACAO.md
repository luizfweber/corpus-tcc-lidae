# Roteiro de verificação do dashboard (equipe LIDAE/NECPF)

> Checklist rápido para conferir as abas que usam dados de egressos, depois de
> qualquer atualização. Feito em 10/07/2026. Os números de referência valem para
> o corpus de 321 TCCs e a base de egressos da DTI de 10/07/2026; se o corpus
> mudou, os valores mudam junto (confira a tendência, não o número exato).

**App público:** https://corpus-tcc-lidae.streamlit.app
**Fonte de egressos (todas as abas):** base individual da DTI, deduplicada por
matrícula, sem matrícula publicada.

## 0. Antes de começar

- [ ] O app abre e mostra o cabeçalho "Corpus de TCCs — Licenciaturas UFRR" com
      os KPIs no topo (TCCs, Grupos, Mediana de páginas, etc.).
- [ ] O menu lateral "Navegação" lista as três abas de egressos:
      **Distribuição**, **Cobertura de Coleta** e **Registros faltantes**.

## 1. Aba "Distribuição"

Rolar até a seção **"Egressos × TCCs cadastrados — por curso (ano a ano)"**.

- [ ] A legenda diz "egressos (**base DTI**, por ano de saída/colação)".
- [ ] Ao escolher um **Curso** e uma **Faixa de anos**, o gráfico mostra duas
      barras por ano: **Egressos (DTI)** e **TCCs cadastrados**.
- [ ] A tabela abaixo tem colunas Ano, Egressos, TCCs cadastrados, Cobertura.
- [ ] Conferência pontual: em **Insikiran**, ano **2022**, deve haver
      ~51 egressos e ~25 TCCs.

## 2. Aba "Cobertura de Coleta"

- [ ] A legenda diz "Cobertura = TCCs coletados ÷ **egressos da DTI**".
- [ ] Existe o seletor **Período**: "Janela 2015–2025" (padrão) e "Todos os anos".
- [ ] Na janela 2015–2025, a **Cobertura global** é ~**18,6%**.
- [ ] A tabela por curso, do maior para o menor, começa por
      **História (~56%)** e **Música (~48%)**; termina com
      **Geografia, Química, Física e Artes Visuais em 0%** (ainda sem coleta).
- [ ] O gráfico "Egressos (DTI) e TCCs coletados, por ano" mostra duas linhas.

## 3. Aba "Registros faltantes" (a mais sensível)

- [ ] Aparece o aviso de **proteção parcial** no topo: nome, curso, período e
      título são públicos; **matrícula e histórico de matrículas ficam
      protegidos** e não aparecem.
- [ ] Fluxo: escolher **Curso** → **Ano de saída** → **Semestre**.
- [ ] A tabela lista **Egresso · Curso/habilitação · Título no sistema (se
      houver)**. **NÃO deve existir coluna de matrícula.** (Se aparecer
      matrícula, PARE e avise: é falha de proteção.)
- [ ] Cada egresso aparece **uma vez** (mesmo quem tem 2 títulos na DTI; os
      títulos ficam reunidos com " | ").
- [ ] Há o botão **"Baixar esta lista (CSV)"**.
- [ ] Ao final, os três números do curso: total de egressos, já catalogados
      (por nome) e faltantes.

## 4. O que fazer se algo estiver errado

- **Matrícula aparecendo em qualquer aba:** falha grave de LGPD. Avisar
      imediatamente e não compartilhar a tela/print. (O arquivo público é gerado
      por `gerar_egressos_publico.py`, que remove matrícula; rodar de novo.)
- **Aba Registros faltantes diz "Base de egressos não encontrada":** o arquivo
      `dados/canonico/egressos_publico.csv` não foi publicado. Rodar o gerador e
      publicar.
- **Números muito diferentes do esperado:** provável atualização do corpus ou da
      base de egressos. Conferir a data no rodapé dos registros e no Leia-me
      (`dados/LEIA-ME_egressos_DTI.md`).
- **Curva de TCCs por ano:** nunca ler como "aumento de produção docente"; ela
      reflete disponibilidade do acervo coletado (CLAUDE.md §4).

## Lembretes de método (indício, não veredito)

- Egresso da DTI = **saída/colação**, evento distinto da **defesa** do TCC.
- "Faltante" casa egresso e TCC **por nome**: pode haver homônimo ou grafia
      diferente. É indício para orientar a coleta, não prova de ausência.
- Tudo é exploratório, não censitário; o corpus é um piloto desbalanceado.

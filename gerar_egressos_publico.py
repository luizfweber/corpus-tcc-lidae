#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o arquivo PÚBLICO de egressos a partir da base sensível da DTI.

Proteção parcial (decisão do responsável pelos dados, 10/07/2026): o NOME do
egresso pode ser público (TCCs são documentos públicos), mas a MATRÍCULA e o
histórico de matrículas (`matriculas_validas`) ficam protegidos e NÃO entram no
arquivo publicado.

Entrada (sensível, gitignorada):
    dados/_pessoais/egressos_dti_licenciaturas_*.csv   (usa o mais recente)
Saída (publicável, versionada):
    dados/canonico/egressos_publico.csv

Colunas publicadas: grupo_tcc, curso_nome, pessoa_nome, afastamento_permanente,
titulo. Exclui bacharelado explícito (B). Rode de novo quando chegar base nova
da DTI. É idempotente.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
PESSOAIS = BASE / "dados" / "_pessoais"
SAIDA = BASE / "dados" / "canonico" / "egressos_publico.csv"

PUBLICAS = ["grupo_tcc", "curso_nome", "pessoa_nome",
            "afastamento_permanente", "titulo"]
PROTEGIDAS = ["discente_matricula", "matriculas_validas"]  # NUNCA publicar


def main():
    arqs = sorted(PESSOAIS.glob("egressos_dti_licenciaturas_*.csv"))
    if not arqs:
        raise SystemExit(f"[ERRO] Nenhuma base em {PESSOAIS}/ "
                         "(egressos_dti_licenciaturas_*.csv).")
    fonte = arqs[-1]
    d = pd.read_csv(fonte)
    n_linhas = len(d)
    # exclui bacharelado explícito (não é egresso de licenciatura)
    d = d[~d["curso_habilitacao"].astype(str).str.contains(r"\(B\)", na=False)]

    # DEDUPLICA POR EGRESSO (matrícula): a DTI tem pessoas com 2 registros de TCC
    # (2 títulos). Contamos o EGRESSO uma vez; os títulos são reunidos numa linha
    # (" | "). A matrícula é usada só como chave aqui e NÃO entra na saída.
    def _junta_titulos(s):
        vist = {str(x).strip() for x in s if pd.notna(x) and str(x).strip()}
        return " | ".join(sorted(vist))
    d = (d.groupby("discente_matricula", as_index=False)
           .agg({"grupo_tcc": "first", "curso_nome": "first",
                 "pessoa_nome": "first", "afastamento_permanente": "first",
                 "titulo": _junta_titulos}))
    n_egressos = len(d)

    pub = d[PUBLICAS].copy()
    pub.to_csv(SAIDA, index=False)
    vazou = [c for c in PROTEGIDAS if c in pub.columns]
    assert not vazou, f"FALHA DE PROTEÇÃO: coluna sensível no arquivo público: {vazou}"
    print(f"Fonte:  {fonte.name}  ({n_linhas} linhas)")
    print(f"Saída:  {SAIDA.relative_to(BASE)}  ({n_egressos} egressos distintos "
          f"por matrícula; {n_linhas - n_egressos} linhas eram 2º título da mesma pessoa)")
    print(f"Colunas publicadas: {PUBLICAS}")
    print(f"Protegidas (fora): {PROTEGIDAS}")


if __name__ == "__main__":
    main()

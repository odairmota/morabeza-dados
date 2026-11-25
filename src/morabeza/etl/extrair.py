"""Lab 5 · Extrair de quatro fontes.

As fontes estão em data/fontes_s1_2025/. Testa com:
    pytest tests/test_etl_lab5.py -v
"""

import json  # noqa: F401  (vais precisar)
import sqlite3  # noqa: F401

import pandas as pd  # noqa: F401


def ler_vendas_csv(caminho):
    """Lê o CSV de vendas com TUDO como texto (dtype=str), para não perder
    informação antes de limpar."""
    # Lê o CSV mantendo todas as colunas como string para preservar valores sujos antes da limpeza
    return pd.read_csv(caminho, dtype=str)


def ler_produtos_excel(caminho):
    """Lê a folha 'produtos' do Excel."""
    # Lê explicitamente a folha 'produtos' do ficheiro Excel
    return pd.read_excel(caminho, sheet_name="produtos")


def ler_clientes_sqlite(caminho):
    """SELECT * FROM clientes. Dica: pd.read_sql_query(sql, conn)"""
    # Abre a ligação à base de dados SQLite e executa a consulta na tabela clientes
    with sqlite3.connect(caminho) as conn:
        return pd.read_sql_query("SELECT * FROM clientes", conn)


def ler_promocoes_json(caminho):
    """O ficheiro imita a resposta de uma API: os registos estão em 'dados'.
    Se 'estado' não for 'ok', levanta ValueError."""
    # Carrega o JSON e valida o campo 'estado' antes de converter os registos para DataFrame
    with open(caminho, encoding="utf-8") as f:
        dados_api = json.load(f)

    if dados_api.get("estado") != "ok":
        raise ValueError(f"Estado da resposta inválido: {dados_api.get('estado')}")

    return pd.DataFrame(dados_api["dados"])
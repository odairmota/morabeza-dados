"""Laboratório 4 (Sessão 7): painel de vendas da Morabeza com pandas e NumPy.

Trabalha com as tabelas completas de 2024 e 2025: vendas, clientes e produtos.
"""
from pathlib import Path
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# PARTE 1: Carregar e Juntar
# -----------------------------------------------------------------------------


def carregar(pasta):
    """Lê os três ficheiros CSV com os tipos corretos."""
    pasta = Path(pasta)
    vendas = pd.read_csv(pasta / "vendas.csv", parse_dates=["data"])
    clientes = pd.read_csv(pasta / "clientes.csv", parse_dates=["data_registo"])
    produtos = pd.read_csv(pasta / "produtos.csv")

    return vendas, clientes, produtos


def juntar(vendas, clientes, produtos):
    """Junta as tabelas com how="left", selecionando apenas as colunas necessárias,

    e cria a coluna 'total'.
    """
    # Selecionar apenas cliente_id, tipo e ilha dos clientes
    cli_subset = clientes[["cliente_id", "tipo", "ilha"]]

    # Selecionar apenas produto_id, nome e categoria dos produtos (evita duplicar preco_unitario)
    prod_subset = produtos[["produto_id", "nome", "categoria"]]

    # Merges consecutivos com how="left"
    df = vendas.merge(cli_subset, on="cliente_id", how="left")
    df = df.merge(prod_subset, on="produto_id", how="left")

    # Criar a coluna 'total' vetorizada
    df["total"] = df["quantidade"] * df["preco_unitario"]

    return df


# -----------------------------------------------------------------------------
# PARTE 2: Faturação Mensal e Top de Produtos
# -----------------------------------------------------------------------------


def faturacao_mensal_por_ilha(df):
    """Cria a coluna 'mes' em formato YYYY-MM e calcula o pivot table da faturação por ilha."""
    df_temp = df.copy()
    df_temp["mes"] = df_temp["data"].dt.strftime("%Y-%m")

    tabela = df_temp.pivot_table(
        index="mes",
        columns="ilha",
        values="total",
        aggfunc="sum",
        fill_value=0,
    )

    return tabela


def top_produtos(df, n):
    """Agrupa por nome do produto, soma o total, ordena do maior para o menor e devolve os n primeiros."""
    return (
        df.groupby("nome")["total"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )


# -----------------------------------------------------------------------------
# PARTE 3: Quotas e Desconto
# -----------------------------------------------------------------------------


def quota_por_tipo(df):
    """Calcula a percentagem da faturação total por tipo de cliente, arredondado a 1 casa decimal."""
    total_geral = df["total"].sum()
    quota = (df.groupby("tipo")["total"].sum() / total_geral) * 100
    return quota.round(1)


def aplicar_desconto(df):
    """Aplica 5% de desconto em encomendas com quantidade >= 20 usando np.where."""
    df_out = df.copy()
    df_out["total_com_desconto"] = np.where(
        df_out["quantidade"] >= 20,
        df_out["total"] * 0.95,
        df_out["total"],
    )
    return df_out


# -----------------------------------------------------------------------------
# EXTENSÃO OPCIONAL (Se decidires implementar)
# -----------------------------------------------------------------------------


def otimizar_tipos(df):
    """Converte colunas de texto repetitivo em category e reduz o tipo dos inteiros."""
    df_opt = df.copy()

    # Converter colunas de texto repetitivo para category
    cols_cat = ["tipo", "ilha", "categoria", "nome"]
    for col in cols_cat:
        if col in df_opt.columns:
            df_opt[col] = df_opt[col].astype("category")

    # Downcast de colunas numéricas inteiras
    for col in df_opt.select_dtypes(include=["int64", "int32"]).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast="integer")

    return df_opt


def formato_longo(tabela):
    """Reverte a pivot_table para formato longo (144 linhas) usando melt."""
    return tabela.reset_index().melt(
        id_vars="mes",
        var_name="ilha",
        value_name="total",
    )
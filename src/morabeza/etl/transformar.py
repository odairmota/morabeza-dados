"""Lab 5 · Transformar (limpar) as vendas com funções puras.

Função pura = não altera o que recebe e devolve sempre o mesmo para a mesma
entrada. Testa com:
    pytest tests/test_etl_lab5.py -v
"""

import unicodedata

import pandas as pd

ILHAS_VALIDAS = ["Santiago", "São Vicente", "Sal", "Boa Vista", "Fogo", "Santo Antão"]

# abreviaturas que aparecem nos dados (chave já "achatada")
_ALIASES = {
    "stgo": "Santiago",
    "sv": "São Vicente",
    "svicente": "São Vicente",
    "boavista": "Boa Vista",
    "santao": "Santo Antão",
}


def _achatar(texto):
    """(VEM PRONTA) 'S. Vicente ' -> 'svicente' (minúsculas, sem acentos,
    só letras e números)."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(ch for ch in sem_acentos.lower() if ch.isalnum())


_CANON = {_achatar(i): i for i in ILHAS_VALIDAS} | _ALIASES


def normalizar_ilha(texto):
    """'  SAO vicente' -> 'São Vicente'. Ilha não servida, vazia ou None -> None.
    Dica: _CANON.get(_achatar(...))"""
    # Garante que None, valores nulos ou strings vazias devolvem None sem rebentar em _achatar
    if texto is None or (not isinstance(texto, str) and pd.isna(texto)):
        return None
    s = str(texto).strip()
    if not s:
        return None
    # Usa _CANON.get(_achatar(...)) para obter o nome canónico ou None se não for servida
    return _CANON.get(_achatar(s))


def normalizar_data(texto):
    """Aceita '2025-03-01' e '01/03/2025'. Devolve pd.Timestamp; data
    impossível ou vazia -> pd.NaT. Dica: pd.to_datetime(..., format=..., errors="coerce")"""
    if texto is None or (not isinstance(texto, str) and pd.isna(texto)):
        return pd.NaT
    s = str(texto).strip()
    if not s:
        return pd.NaT

    # Tenta os dois formatos esperados; datas inválidas/impossíveis viram pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        ts = pd.to_datetime(s, format=fmt, errors="coerce")
        if pd.notna(ts):
            return pd.Timestamp(ts)

    return pd.NaT


def limpar_numero(serie):
    """(VEM PRONTA) '12 un' -> 12.0, '1250 CVE' -> 1250.0, '' -> NaN.
    A expressão regular apanha o primeiro número (com casas decimais opcionais)."""
    return (serie.astype("string")
                 .str.extract(r"(\d+(?:[.,]\d+)?)", expand=False)
                 .str.replace(",", ".", regex=False)
                 .astype(float))


def remover_duplicados(df):
    """Remove linhas com venda_id repetido (fica a primeira)."""
    # Devolve cópia sem duplicados de venda_id sem alterar o df original
    return df.drop_duplicates(subset=["venda_id"], keep="first").copy()


def limpar_vendas(df):
    """Junta tudo. NÃO altera o df original (usa .assign ou .copy()).
    Passos:
1. remover duplicados
2. normalizar ilha e data; limpar quantidade e preco_unitario
3. remover linhas onde algum destes quatro ficou vazio
4. quantidade e preco_unitario como int
    """
    # 1. remover duplicados
    sem_dup = remover_duplicados(df)

    # 2. normalizar ilha e data; limpar quantidade e preco_unitario (sem mutar o original)
    limpo = sem_dup.assign(
        ilha=sem_dup["ilha"].map(normalizar_ilha),
        data=sem_dup["data"].map(normalizar_data),
        quantidade=limpar_numero(sem_dup["quantidade"]),
        preco_unitario=limpar_numero(sem_dup["preco_unitario"]),
    )

    # 3. remover linhas onde algum destes quatro ficou vazio
    limpo = limpo.dropna(subset=["ilha", "data", "quantidade", "preco_unitario"]).copy()

    # 4. quantidade e preco_unitario como int
    return limpo.assign(
        quantidade=limpo["quantidade"].astype(int),
        preco_unitario=limpo["preco_unitario"].astype(int),
    )


if __name__ == "__main__":
    print(pd.__version__)
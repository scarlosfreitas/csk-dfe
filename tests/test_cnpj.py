"""Testes do hash de segmentação do CNPJ, spec `hash-cnpj`."""

from __future__ import annotations

import pytest

from csk_dfe import CnpjInvalidoError, hash_cnpj


# --- Vetores normativos (6.1) --------------------------------------------


@pytest.mark.parametrize(
    "raiz,segmento_esperado",
    [
        ("11111111", 13),
        ("22222222", 5),
        ("99999999", 29),
        ("ABCDEFGH", 13),
        ("1111111A", 61),
    ],
)
def test_vetores_normativos_do_hash(raiz, segmento_esperado):
    assert hash_cnpj(raiz) == segmento_esperado


def test_sensibilidade_a_um_unico_caractere():
    assert hash_cnpj("11111111") != hash_cnpj("1111111A")


# --- Faixa do segmento (6.2) ----------------------------------------------


def test_segmento_sempre_na_faixa_0_a_63():
    raizes = [f"{n:08d}" for n in range(0, 100_000, 137)]
    for raiz in raizes:
        assert 0 <= hash_cnpj(raiz) <= 63


# --- Escopo da raiz de 8 caracteres (6.3) ----------------------------------


def test_cnpj_completo_e_raiz_coincidem():
    raiz = "12345678"
    cnpj_completo = raiz + "000191"
    assert hash_cnpj(cnpj_completo) == hash_cnpj(raiz)


def test_filiais_do_mesmo_contribuinte_produzem_o_mesmo_segmento():
    raiz = "12345678"
    matriz = raiz + "000191"
    filial = raiz + "000272"
    assert hash_cnpj(matriz) == hash_cnpj(filial)


# --- CNPJ formatado (6.4) --------------------------------------------------


def test_cnpj_formatado_produz_o_mesmo_segmento_do_nao_formatado():
    formatado = "11.111.111/0001-91"
    nao_formatado = "11111111000191"
    assert hash_cnpj(formatado) == hash_cnpj(nao_formatado)


# --- Raízes alfanuméricas (6.5) --------------------------------------------


def test_raiz_alfanumerica_e_aceita():
    assert 0 <= hash_cnpj("ABCDEFGH") <= 63


def test_caixa_do_caractere_altera_o_segmento():
    # "abcdefgh" colide por acaso com "ABCDEFGH" no segmento 13 após o `& 63`,
    # apesar dos hashes de 32 bits completos serem diferentes — ver design.md.
    assert hash_cnpj("ABCDEFGH") != hash_cnpj("ABCDEFGh")


# --- Rejeição de entrada insuficiente (6.6) --------------------------------


def test_entrada_vazia_e_rejeitada():
    with pytest.raises(CnpjInvalidoError):
        hash_cnpj("")


def test_entrada_curta_demais_e_rejeitada():
    with pytest.raises(CnpjInvalidoError):
        hash_cnpj("1234567")


def test_entrada_curta_apos_normalizacao_e_rejeitada():
    with pytest.raises(CnpjInvalidoError):
        hash_cnpj("12.345.6")

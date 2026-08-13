"""Testes da codificação Base62 de largura fixa, spec `base62`."""

from __future__ import annotations

import string

import pytest

from csk_dfe import Base62InvalidoError, from_base62, to_base62

_ALFABETO = set(string.digits + string.ascii_uppercase + string.ascii_lowercase)


# --- Largura fixa (8.1, 8.2, 8.3) ------------------------------------------


@pytest.mark.parametrize("csk", [0, 1, 220101 * 2**43, 2**62, 2**63 - 1])
def test_codificacao_tem_11_caracteres_do_alfabeto(csk):
    texto = to_base62(csk)
    assert len(texto) == 11
    assert set(texto) <= _ALFABETO


def test_padding_de_chave_de_baixa_magnitude():
    texto = to_base62(101 * 2**43)
    assert len(texto) == 11
    assert texto[:2] == "00"


def test_chave_zero_e_11_caracteres_zero():
    assert to_base62(0) == "0" * 11


# --- Ordenação preservada (8.4) --------------------------------------------


def test_ordem_lexicografica_entre_duas_chaves():
    a, b = 220101 * 2**43, 230101 * 2**43
    assert a < b
    assert to_base62(a) < to_base62(b)


def test_ordem_preservada_em_um_conjunto_variado():
    chaves = [0, 5, 101 * 2**43, 2**30, 2**40, 2**50, 2**62, 2**63 - 1]
    textos_ordenados = sorted(to_base62(csk) for csk in chaves)
    esperado = [to_base62(csk) for csk in sorted(chaves)]
    assert textos_ordenados == esperado


# --- Ida e volta (8.5) ------------------------------------------------------


@pytest.mark.parametrize("csk", [0, 1, 220101 * 2**43, 2**62, 2**63 - 1])
def test_ida_e_volta(csk):
    assert from_base62(to_base62(csk)) == csk


# --- Rejeição de texto inválido (8.6) ---------------------------------------


def test_rejeita_texto_vazio():
    with pytest.raises(Base62InvalidoError):
        from_base62("")


@pytest.mark.parametrize("texto", ["0" * 10, "0" * 12])
def test_rejeita_comprimento_diferente_de_11(texto):
    with pytest.raises(Base62InvalidoError):
        from_base62(texto)


def test_rejeita_caractere_fora_do_alfabeto():
    with pytest.raises(Base62InvalidoError):
        from_base62("0000000000!")


def test_rejeita_valor_que_excede_a_faixa_da_chave():
    texto = to_base62(2**63 - 1)
    maior_texto = "z" * 11
    assert maior_texto > texto
    with pytest.raises(Base62InvalidoError):
        from_base62(maior_texto)

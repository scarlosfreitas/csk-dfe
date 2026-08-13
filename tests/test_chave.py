"""Testes de composição e decomposição da chave CSK-DFE, spec `chave-composta`."""

from __future__ import annotations

import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

from csk_dfe import (
    ChaveInvalidaError,
    CskDecodificado,
    DataInvalidaError,
    TabelaEstendidaError,
    TpDoc,
    decode,
    generate,
    hash_cnpj,
)

RAIZ = Path(__file__).resolve().parent.parent
CNPJ = "11.111.111/0001-91"
TPDOC = TpDoc.from_cod(5)


# --- Composição da chave (7.1, 7.2, 7.3) -----------------------------------


def test_identidade_aritmetica_da_chave():
    csk = generate("220101", TPDOC, CNPJ)
    d = decode(csk)
    aammdd = int(d.data.strftime("%y%m%d"))
    reverso = d.tpdoc.get_reverse_cod()
    esperado = aammdd * 2**43 + reverso * 2**36 + d.hash_cnpj * 2**30 + d.random_number
    assert csk == esperado


def test_bit_63_e_sempre_zero():
    csk = generate("991231", TPDOC, CNPJ)
    assert csk >> 63 == 0


def test_campo_de_documento_grava_o_codigo_reverso():
    tpdoc = TpDoc.from_cod(5)
    assert tpdoc.get_reverse_cod() == 80
    csk = generate("220101", tpdoc, CNPJ)
    campo_documento = (csk >> 36) & 0x7F
    assert campo_documento == 80


# --- Formas aceitas da data do documento (7.4) ------------------------------


def test_date_datetime_e_string_do_mesmo_dia_produzem_o_mesmo_campo_de_data():
    csk_str = generate("220101", TPDOC, CNPJ)
    csk_date = generate(date(2022, 1, 1), TPDOC, CNPJ)
    csk_datetime = generate(datetime(2022, 1, 1, 23, 59, 59), TPDOC, CNPJ)

    campo_data = lambda csk: (csk >> 43) & 0xFFFFF
    assert campo_data(csk_str) == campo_data(csk_date) == campo_data(csk_datetime) == 220101


def test_string_fora_do_formato_e_rejeitada():
    with pytest.raises(DataInvalidaError):
        generate("22-01-01", TPDOC, CNPJ)


# --- Particionamento e ordenação por data (7.5, 7.6) -----------------------


def test_faixa_de_um_dia():
    csk = generate("220101", TPDOC, CNPJ)
    assert 220101 * 2**43 <= csk < 220102 * 2**43


def test_ordenacao_cronologica_entre_anos():
    for _ in range(20):
        csk_2022 = generate("221231", TPDOC, CNPJ)
        csk_2023 = generate("230101", TPDOC, CNPJ)
        assert csk_2022 < csk_2023


# --- Rejeição de datas inválidas (7.7, 7.8) ---------------------------------


@pytest.mark.parametrize("data_invalida", ["991331", "220230", "000000"])
def test_rejeita_datas_inexistentes_no_calendario(data_invalida):
    with pytest.raises(DataInvalidaError):
        generate(data_invalida, TPDOC, CNPJ)


def test_rejeita_data_anterior_a_janela_de_seculo():
    with pytest.raises(DataInvalidaError):
        generate(date(1999, 12, 31), TPDOC, CNPJ)


def test_rejeita_data_posterior_a_janela_de_seculo():
    with pytest.raises(DataInvalidaError):
        generate(date(2100, 1, 1), TPDOC, CNPJ)


# --- Ida e volta e decode() (7.9, 7.10) -------------------------------------


def test_ida_e_volta_de_generate_para_decode():
    tpdoc = TpDoc.from_cod(15)
    csk = generate(date(2022, 6, 15), tpdoc, CNPJ)
    decodificado = decode(csk)
    assert decodificado.data == date(2022, 6, 15)
    assert decodificado.tpdoc == tpdoc
    assert decodificado.hash_cnpj == hash_cnpj(CNPJ)


def test_decode_de_campo_de_data_220101_devolve_01_01_2022():
    csk = 220101 * 2**43
    assert decode(csk).data == date(2022, 1, 1)


# --- Número de desambiguação (7.11, 7.12, 7.13) -----------------------------


def test_chamadas_consecutivas_produzem_chaves_diferentes():
    csk1 = generate("220101", TPDOC, CNPJ)
    csk2 = generate("220101", TPDOC, CNPJ)
    assert csk1 != csk2


def test_extremos_do_random_number(monkeypatch):
    import csk_dfe.chave as chave_mod

    monkeypatch.setattr(chave_mod.random, "getrandbits", lambda n: 0)
    csk_min = generate("220101", TPDOC, CNPJ)
    assert decode(csk_min).random_number == 0
    assert decode(csk_min).hash_cnpj == hash_cnpj(CNPJ)

    monkeypatch.setattr(chave_mod.random, "getrandbits", lambda n: 2**30 - 1)
    csk_max = generate("220101", TPDOC, CNPJ)
    assert decode(csk_max).random_number == 2**30 - 1
    assert decode(csk_max).hash_cnpj == hash_cnpj(CNPJ)


def test_random_number_nao_forma_progressao():
    valores = [decode(generate("220101", TPDOC, CNPJ)).random_number for _ in range(10)]
    diferencas = [b - a for a, b in zip(valores, valores[1:])]
    assert len(set(diferencas)) > 1


# --- Validação na decomposição (7.14, 7.15) ---------------------------------


def test_decode_rejeita_valor_negativo():
    with pytest.raises(ChaveInvalidaError):
        decode(-1)


def test_decode_rejeita_valor_com_bit_de_sinal_ocupado():
    with pytest.raises(ChaveInvalidaError):
        decode(2**63)


def test_decode_rejeita_campo_de_data_sem_correspondencia_no_calendario():
    csk = 991331 * 2**43
    with pytest.raises(ChaveInvalidaError):
        decode(csk)


def test_decode_rejeita_campo_de_documento_de_tabela_estendida():
    csk = 220101 * 2**43 + 1 * 2**36
    with pytest.raises(TabelaEstendidaError):
        decode(csk)


# --- CskDecodificado desempacotável (7.16) ----------------------------------


def test_cskdecodificado_e_desempacotavel_posicionalmente():
    csk = generate("220101", TPDOC, CNPJ)
    data, tpdoc, h, n = decode(csk)
    d = decode(csk)
    assert (data, tpdoc, h, n) == (d.data, d.tpdoc, d.hash_cnpj, d.random_number)
    assert isinstance(d, CskDecodificado)


# --- Geração sem CNPJ (28) ---------------------------------------------------


def test_chave_gerada_sem_cnpj():
    csk = generate("220101", TPDOC)
    assert csk > 0
    assert csk >> 63 == 0
    assert 220101 * 2**43 <= csk < 220102 * 2**43

    d = decode(csk)
    assert d.data == date(2022, 1, 1)
    assert d.tpdoc == TPDOC


def test_faixa_dos_36_bits_aleatorios_sem_cnpj(monkeypatch):
    import csk_dfe.chave as chave_mod

    monkeypatch.setattr(chave_mod.random, "getrandbits", lambda n: 0)
    csk_min = generate("220101", TPDOC)
    assert csk_min & 0xFFFFFFFFF == 0
    assert (csk_min >> 36) & 0x7F == TPDOC.get_reverse_cod()

    monkeypatch.setattr(chave_mod.random, "getrandbits", lambda n: 2**36 - 1)
    csk_max = generate("220101", TPDOC)
    assert csk_max & 0xFFFFFFFFF == 2**36 - 1
    assert (csk_max >> 36) & 0x7F == TPDOC.get_reverse_cod()


def test_chaves_distintas_sem_cnpj():
    csk1 = generate("220101", TPDOC)
    csk2 = generate("220101", TPDOC)
    assert csk1 != csk2


def test_decomposicao_de_chave_gerada_sem_cnpj():
    csk = generate("220101", TPDOC)
    d = decode(csk)
    assert 0 <= d.hash_cnpj <= 63


def test_ida_e_volta_sem_cnpj():
    tpdoc = TpDoc.from_cod(15)
    csk = generate(date(2022, 6, 15), tpdoc)
    d = decode(csk)
    assert d.data == date(2022, 6, 15)
    assert d.tpdoc == tpdoc


@pytest.mark.parametrize("data_invalida", ["991331", "220230", "000000"])
def test_rejeicao_de_datas_invalidas_sem_cnpj(data_invalida):
    with pytest.raises(DataInvalidaError):
        generate(data_invalida, TPDOC)


def test_particionamento_preservado_sem_cnpj():
    csk = generate("220101", TPDOC)
    assert 220101 * 2**43 <= csk < 220102 * 2**43


def test_ordenacao_cronologica_entre_anos_com_e_sem_cnpj():
    for _ in range(20):
        csk_2022_com_cnpj = generate("221231", TPDOC, CNPJ)
        csk_2022_sem_cnpj = generate("221231", TPDOC)
        csk_2023_com_cnpj = generate("230101", TPDOC, CNPJ)
        csk_2023_sem_cnpj = generate("230101", TPDOC)
        assert csk_2022_com_cnpj < csk_2023_com_cnpj
        assert csk_2022_com_cnpj < csk_2023_sem_cnpj
        assert csk_2022_sem_cnpj < csk_2023_com_cnpj
        assert csk_2022_sem_cnpj < csk_2023_sem_cnpj


# --- Ausência de marcador de origem (29) -------------------------------------


def test_nenhum_campo_distingue_as_duas_origens():
    csk_com_cnpj = generate("220101", TPDOC, CNPJ)
    csk_sem_cnpj = generate("220101", TPDOC)
    d_com = decode(csk_com_cnpj)
    d_sem = decode(csk_sem_cnpj)
    assert type(d_com) is type(d_sem)
    assert d_com._fields == d_sem._fields


# --- Lote DFe e data de recepção (30) -----------------------------------------


def test_data_de_recepcao_em_lote_de_dfe():
    lote_dfe = TpDoc.from_name("Lote DFe")
    csk = generate("220101", lote_dfe, CNPJ)
    campo_data = (csk >> 43) & 0xFFFFF
    assert campo_data == 220101


# --- Ausência de I/O e dependências (7.17, 7.18) ----------------------------


def test_generate_e_decode_nao_abrem_arquivos(monkeypatch):
    import builtins

    def open_proibido(*args, **kwargs):
        raise AssertionError("generate()/decode() não devem abrir arquivos")

    monkeypatch.setattr(builtins, "open", open_proibido)

    csk = generate("220101", TPDOC, CNPJ)
    decode(csk)


def test_pacote_gera_chaves_em_ambiente_com_apenas_a_stdlib():
    src = str(RAIZ / "src")
    codigo = (
        "import csk_dfe; "
        "csk = csk_dfe.generate('220101', csk_dfe.TpDoc.from_cod(5), '11111111000191'); "
        "assert isinstance(csk, int)"
    )
    resultado = subprocess.run(
        [sys.executable, "-S", "-c", codigo],
        env={"PYTHONPATH": src},
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stderr

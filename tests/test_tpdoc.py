"""Testes da resolução de tipos de documento (`TpDoc`), spec `tipo-documento`."""

from __future__ import annotations

import builtins
import csv
from pathlib import Path

import pytest

from csk_dfe import (
    CodigoForaDaFaixaError,
    NomeInexistenteError,
    ReversoForaDaFaixaError,
    TabelaEstendidaError,
    TpDoc,
)
from csk_dfe import _tabela_tpdoc

RAIZ = Path(__file__).resolve().parent.parent
CSV_REFERENCIA = RAIZ / "references" / "domain" / "tab-tpdoc.csv"


# --- Resolução por código (5.1) ---------------------------------------


def test_codigo_valido_tabela_base():
    tipo = TpDoc.from_cod(0)
    assert tipo.get_cod() == 0
    assert tipo.get_reverse_cod() == 0
    assert tipo.get_name() == "NFe"


def test_codigo_valido_sem_nome_atribuido():
    tipo = TpDoc.from_cod(2)
    assert tipo.get_cod() == 2
    assert tipo.get_reverse_cod() == 32
    assert tipo.get_name() == ""


@pytest.mark.parametrize("codigo", [-1, 64, 999])
def test_codigo_fora_da_faixa_e_rejeitado(codigo):
    with pytest.raises(CodigoForaDaFaixaError):
        TpDoc.from_cod(codigo)


# --- Resolução por código reverso (5.2) --------------------------------


def test_codigo_reverso_conhecido():
    tipo = TpDoc.from_reverse_cod(80)
    assert tipo.get_cod() == 5
    assert tipo.get_name() == "NFCe"


@pytest.mark.parametrize("reverso", [1, 3, 127])
def test_codigo_reverso_impar_e_rejeitado_como_tabela_estendida(reverso):
    with pytest.raises(TabelaEstendidaError):
        TpDoc.from_reverse_cod(reverso)


@pytest.mark.parametrize("reverso", [-1, 128, 999])
def test_codigo_reverso_fora_de_7_bits_e_rejeitado(reverso):
    with pytest.raises(ReversoForaDaFaixaError):
        TpDoc.from_reverse_cod(reverso)


# --- Resolução por nome (5.3) -------------------------------------------


def test_nome_atribuido():
    tipo = TpDoc.from_name("MDFe")
    assert tipo.get_cod() == 15
    assert tipo.get_reverse_cod() == 120


def test_nome_inexistente_e_rejeitado():
    with pytest.raises(NomeInexistenteError):
        TpDoc.from_name("documento-que-nao-existe")


def test_nome_vazio_e_rejeitado_mesmo_com_reservados_na_tabela():
    with pytest.raises(NomeInexistenteError):
        TpDoc.from_name("")


# --- Regra de reversão de 7 bits (5.4, 5.5, 5.6) ------------------------


@pytest.mark.parametrize(
    "codigo,reverso_esperado",
    [(0, 0), (1, 64), (5, 80), (16, 4), (32, 2), (63, 126)],
)
def test_vetores_da_regra_de_reversao(codigo, reverso_esperado):
    assert TpDoc.from_cod(codigo).get_reverse_cod() == reverso_esperado


def test_reversos_sao_pares_e_distintos():
    reversos = [TpDoc.from_cod(codigo).get_reverse_cod() for codigo in range(64)]
    assert all(reverso % 2 == 0 for reverso in reversos)
    assert len(set(reversos)) == 64


def test_ida_e_volta_entre_codigo_e_codigo_reverso():
    for codigo in range(64):
        original = TpDoc.from_cod(codigo)
        obtido = TpDoc.from_reverse_cod(original.get_reverse_cod())
        assert obtido == original


# --- Aderência à fonte da verdade (5.7, 5.8) -----------------------------


def test_tabela_gerada_e_sincronizada_com_o_csv():
    with CSV_REFERENCIA.open(newline="", encoding="utf-8") as arquivo:
        linhas_csv = {
            int(linha["codigo"]): (int(linha["reverso"]), linha["Tipo"].strip())
            for linha in csv.DictReader(arquivo)
        }

    for entrada in _tabela_tpdoc.ENTRADAS:
        reverso_csv, nome_csv = linhas_csv[entrada.codigo]
        assert entrada.reverso == reverso_csv
        assert entrada.nome == nome_csv


def test_tabela_tem_64_entradas_sem_lacunas_nem_repeticoes():
    codigos = [entrada.codigo for entrada in _tabela_tpdoc.ENTRADAS]
    assert len(codigos) == 64
    assert sorted(codigos) == list(range(64))


# --- Ausência de I/O e de dependências externas (5.9, 5.10) --------------


def test_resolucao_nao_abre_arquivos(monkeypatch):
    def open_proibido(*args, **kwargs):
        raise AssertionError("resolução de TpDoc não deve abrir arquivos")

    monkeypatch.setattr(builtins, "open", open_proibido)

    TpDoc.from_cod(5)
    TpDoc.from_reverse_cod(80)
    TpDoc.from_name("NFCe")


def test_pacote_importa_sem_dependencias_externas():
    import subprocess
    import sys

    src = str(RAIZ / "src")
    resultado = subprocess.run(
        [sys.executable, "-S", "-c", "import csk_dfe"],
        env={"PYTHONPATH": src},
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stderr

"""Composição e decomposição do CSK-DFE, a chave de 64 bits."""

from __future__ import annotations

import random
from datetime import date, datetime
from typing import NamedTuple, Union

from .cnpj import hash_cnpj
from .excecoes import ChaveInvalidaError, DataInvalidaError
from .tpdoc import TpDoc

_DESLOCAMENTO_DATA = 43
_DESLOCAMENTO_DOCUMENTO = 36
_DESLOCAMENTO_CNPJ = 30

_LARGURA_DATA = 20
_LARGURA_DOCUMENTO = 7
_LARGURA_CNPJ = 6
_LARGURA_RANDOM = 30

_MASCARA_DATA = (1 << _LARGURA_DATA) - 1
_MASCARA_DOCUMENTO = (1 << _LARGURA_DOCUMENTO) - 1
_MASCARA_CNPJ = (1 << _LARGURA_CNPJ) - 1
_MASCARA_RANDOM = (1 << _LARGURA_RANDOM) - 1

_LIMITE_CHAVE = 2**63
_ANO_MINIMO = 2000
_ANO_MAXIMO = 2099

DhEmi = Union[datetime, date, str]


class CskDecodificado(NamedTuple):
    """Os quatro campos decompostos de uma chave CSK-DFE."""

    dhemi: date
    tpdoc: TpDoc
    hash_cnpj: int
    random_number: int


def _normalizar_dhemi(dhemi: DhEmi) -> int:
    if isinstance(dhemi, datetime):
        data = dhemi.date()
    elif isinstance(dhemi, date):
        data = dhemi
    elif isinstance(dhemi, str):
        if len(dhemi) != 6 or not dhemi.isdigit():
            raise DataInvalidaError(
                f"data {dhemi!r} não está no formato AAMMDD de 6 dígitos"
            )
        ano, mes, dia = int(dhemi[0:2]), int(dhemi[2:4]), int(dhemi[4:6])
        try:
            data = date(2000 + ano, mes, dia)
        except ValueError as erro:
            raise DataInvalidaError(f"data {dhemi!r} não é um dia real do calendário") from erro
    else:
        raise DataInvalidaError(f"tipo {type(dhemi)!r} não é aceito para dhemi")

    if not _ANO_MINIMO <= data.year <= _ANO_MAXIMO:
        raise DataInvalidaError(
            f"data {data.isoformat()} fora da janela de século {_ANO_MINIMO}–{_ANO_MAXIMO}"
        )

    return (data.year - 2000) * 10000 + data.month * 100 + data.day


def generate(dhemi: DhEmi, tpdoc: TpDoc, cnpj: str) -> int:
    """Compõe a chave CSK-DFE de 64 bits a partir da data de emissão, do tipo de documento e do CNPJ.

    `dhemi` aceita `datetime` (a hora é descartada), `date` ou string `AAMMDD`.
    Os 30 bits menos significativos vêm de um gerador não criptográfico:
    chamadas repetidas com os mesmos argumentos produzem chaves diferentes, e
    a biblioteca não garante unicidade.
    """
    aammdd = _normalizar_dhemi(dhemi)
    segmento = hash_cnpj(cnpj)
    random_number = random.getrandbits(_LARGURA_RANDOM)

    return (
        (aammdd << _DESLOCAMENTO_DATA)
        + (tpdoc.get_reverse_cod() << _DESLOCAMENTO_DOCUMENTO)
        + (segmento << _DESLOCAMENTO_CNPJ)
        + random_number
    )


def decode(csk: int) -> CskDecodificado:
    """Decompõe uma chave CSK-DFE válida em `CskDecodificado(dhemi, tpdoc, hash_cnpj, random_number)`.

    O CNPJ não é recuperável a partir da chave: `hash_cnpj` é o segmento de
    0 a 63 do hash, nunca o CNPJ original.
    """
    if csk < 0 or csk >= _LIMITE_CHAVE:
        raise ChaveInvalidaError(f"valor {csk} não é uma chave CSK-DFE válida de 63 bits")

    aammdd = (csk >> _DESLOCAMENTO_DATA) & _MASCARA_DATA
    reverso = (csk >> _DESLOCAMENTO_DOCUMENTO) & _MASCARA_DOCUMENTO
    segmento = (csk >> _DESLOCAMENTO_CNPJ) & _MASCARA_CNPJ
    random_number = csk & _MASCARA_RANDOM

    ano, resto = divmod(aammdd, 10000)
    mes, dia = divmod(resto, 100)
    try:
        dhemi = date(2000 + ano, mes, dia)
    except ValueError as erro:
        raise ChaveInvalidaError(
            f"campo de data {aammdd:06d} não é um dia real do calendário"
        ) from erro

    tpdoc = TpDoc.from_reverse_cod(reverso)

    return CskDecodificado(dhemi=dhemi, tpdoc=tpdoc, hash_cnpj=segmento, random_number=random_number)

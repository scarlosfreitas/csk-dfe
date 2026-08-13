"""Exceções de domínio do CSK-DFE."""

from __future__ import annotations


class CskDfeError(ValueError):
    """Base de todas as exceções de domínio do pacote."""


class TpDocError(CskDfeError):
    """Base das exceções de domínio de `TpDoc`."""


class CodigoForaDaFaixaError(TpDocError):
    """Código de domínio fora da faixa 0 a 63."""


class ReversoForaDaFaixaError(TpDocError):
    """Código reverso fora da faixa 0 a 127."""


class TabelaEstendidaError(TpDocError):
    """Código reverso ímpar: sinaliza um documento de tabela estendida, fora de escopo."""


class NomeInexistenteError(TpDocError):
    """Nome não presente na tabela de tipos de documento."""


class CnpjInvalidoError(CskDfeError):
    """CNPJ ou raiz de CNPJ inválidos para o cálculo do hash de segmentação."""


class DataInvalidaError(CskDfeError):
    """Data de emissão inválida: fora do calendário ou fora da janela 2000–2099."""


class ChaveInvalidaError(CskDfeError):
    """Valor que não corresponde a uma chave CSK-DFE válida."""


class Base62InvalidoError(CskDfeError):
    """Texto Base62 inválido para decodificação em uma chave CSK-DFE."""

"""Exceções de domínio para a resolução de tipos de documento."""

from __future__ import annotations


class TpDocError(ValueError):
    """Base das exceções de domínio de `TpDoc`."""


class CodigoForaDaFaixaError(TpDocError):
    """Código de domínio fora da faixa 0 a 63."""


class ReversoForaDaFaixaError(TpDocError):
    """Código reverso fora da faixa 0 a 127."""


class TabelaEstendidaError(TpDocError):
    """Código reverso ímpar: sinaliza um documento de tabela estendida, fora de escopo."""


class NomeInexistenteError(TpDocError):
    """Nome não presente na tabela de tipos de documento."""

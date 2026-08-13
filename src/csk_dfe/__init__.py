"""csk_dfe — Composite Sharding Key para documentos fiscais eletrônicos brasileiros."""

from .excecoes import (
    CodigoForaDaFaixaError,
    NomeInexistenteError,
    ReversoForaDaFaixaError,
    TabelaEstendidaError,
    TpDocError,
)
from .tpdoc import TpDoc

__all__ = [
    "TpDoc",
    "TpDocError",
    "CodigoForaDaFaixaError",
    "ReversoForaDaFaixaError",
    "TabelaEstendidaError",
    "NomeInexistenteError",
]

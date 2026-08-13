"""csk_dfe — Composite Sharding Key para documentos fiscais eletrônicos brasileiros."""

from .base62 import from_base62, to_base62
from .chave import CskDecodificado, decode, generate
from .cnpj import hash_cnpj
from .excecoes import (
    Base62InvalidoError,
    ChaveInvalidaError,
    CnpjInvalidoError,
    CodigoForaDaFaixaError,
    CskDfeError,
    DataInvalidaError,
    NomeInexistenteError,
    ReversoForaDaFaixaError,
    TabelaEstendidaError,
    TpDocError,
)
from .tpdoc import TpDoc

__all__ = [
    "TpDoc",
    "CskDecodificado",
    "generate",
    "decode",
    "hash_cnpj",
    "to_base62",
    "from_base62",
    "CskDfeError",
    "TpDocError",
    "CodigoForaDaFaixaError",
    "ReversoForaDaFaixaError",
    "TabelaEstendidaError",
    "NomeInexistenteError",
    "CnpjInvalidoError",
    "DataInvalidaError",
    "ChaveInvalidaError",
    "Base62InvalidoError",
]

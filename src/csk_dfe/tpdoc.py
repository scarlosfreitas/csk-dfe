"""Resolução de tipos de documento fiscal do CSK-DFE."""

from __future__ import annotations

from dataclasses import dataclass

from . import _tabela_tpdoc
from .excecoes import (
    CodigoForaDaFaixaError,
    NomeInexistenteError,
    ReversoForaDaFaixaError,
    TabelaEstendidaError,
)


@dataclass(frozen=True)
class TpDoc:
    """Um tipo de documento fiscal, identificado por código, código reverso e nome."""

    codigo: int
    reverso: int
    nome: str

    @classmethod
    def from_cod(cls, codigo: int) -> TpDoc:
        entrada = _tabela_tpdoc.POR_CODIGO.get(codigo)
        if entrada is None:
            raise CodigoForaDaFaixaError(
                f"código {codigo} fora da faixa 0 a 63"
            )
        return cls(entrada.codigo, entrada.reverso, entrada.nome)

    @classmethod
    def from_reverse_cod(cls, reverso: int) -> TpDoc:
        if not 0 <= reverso <= 127:
            raise ReversoForaDaFaixaError(
                f"código reverso {reverso} fora da faixa 0 a 127"
            )
        if reverso & 1:
            raise TabelaEstendidaError(
                f"código reverso {reverso} é ímpar: sinaliza tabela estendida, fora de escopo"
            )
        entrada = _tabela_tpdoc.POR_REVERSO[reverso]
        return cls(entrada.codigo, entrada.reverso, entrada.nome)

    @classmethod
    def from_name(cls, nome: str) -> TpDoc:
        entrada = _tabela_tpdoc.POR_NOME.get(nome) if nome else None
        if entrada is None:
            raise NomeInexistenteError(f"nome {nome!r} não consta da tabela de tipos de documento")
        return cls(entrada.codigo, entrada.reverso, entrada.nome)

    def get_cod(self) -> int:
        return self.codigo

    def get_reverse_cod(self) -> int:
        return self.reverso

    def get_name(self) -> str:
        return self.nome

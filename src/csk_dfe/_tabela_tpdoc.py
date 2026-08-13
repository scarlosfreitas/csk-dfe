"""Tabela de tipos de documento fiscal do CSK-DFE.

Gerado por `scripts/gerar_tabela_tpdoc.py` a partir de
`references/domain/tab-tpdoc.csv`, que é a fonte da verdade. NÃO EDITE ESTE
ARQUIVO À MÃO — edite o CSV e rode o gerador novamente.
"""

from __future__ import annotations

from typing import NamedTuple


class _EntradaTpDoc(NamedTuple):
    codigo: int
    reverso: int
    nome: str

ENTRADAS: tuple[_EntradaTpDoc, ...] = (
    _EntradaTpDoc(0, 0, "NFe"),
    _EntradaTpDoc(1, 64, "NFe Evento"),
    _EntradaTpDoc(2, 32, ""),
    _EntradaTpDoc(3, 96, ""),
    _EntradaTpDoc(4, 16, ""),
    _EntradaTpDoc(5, 80, "NFCe"),
    _EntradaTpDoc(6, 48, "NFCe Evento"),
    _EntradaTpDoc(7, 112, ""),
    _EntradaTpDoc(8, 8, ""),
    _EntradaTpDoc(9, 72, ""),
    _EntradaTpDoc(10, 40, "CTe"),
    _EntradaTpDoc(11, 104, "CTe Evento"),
    _EntradaTpDoc(12, 24, ""),
    _EntradaTpDoc(13, 88, ""),
    _EntradaTpDoc(14, 56, ""),
    _EntradaTpDoc(15, 120, "MDFe"),
    _EntradaTpDoc(16, 4, "MDFe Evento"),
    _EntradaTpDoc(17, 68, ""),
    _EntradaTpDoc(18, 36, ""),
    _EntradaTpDoc(19, 100, ""),
    _EntradaTpDoc(20, 20, ""),
    _EntradaTpDoc(21, 84, ""),
    _EntradaTpDoc(22, 52, ""),
    _EntradaTpDoc(23, 116, ""),
    _EntradaTpDoc(24, 12, ""),
    _EntradaTpDoc(25, 76, ""),
    _EntradaTpDoc(26, 44, ""),
    _EntradaTpDoc(27, 108, ""),
    _EntradaTpDoc(28, 28, ""),
    _EntradaTpDoc(29, 92, ""),
    _EntradaTpDoc(30, 60, ""),
    _EntradaTpDoc(31, 124, "Lote DFe"),
    _EntradaTpDoc(32, 2, "EFD"),
    _EntradaTpDoc(33, 66, ""),
    _EntradaTpDoc(34, 34, ""),
    _EntradaTpDoc(35, 98, ""),
    _EntradaTpDoc(36, 18, "PGDASD"),
    _EntradaTpDoc(37, 82, ""),
    _EntradaTpDoc(38, 50, ""),
    _EntradaTpDoc(39, 114, ""),
    _EntradaTpDoc(40, 10, ""),
    _EntradaTpDoc(41, 74, ""),
    _EntradaTpDoc(42, 42, ""),
    _EntradaTpDoc(43, 106, ""),
    _EntradaTpDoc(44, 26, ""),
    _EntradaTpDoc(45, 90, ""),
    _EntradaTpDoc(46, 58, ""),
    _EntradaTpDoc(47, 122, ""),
    _EntradaTpDoc(48, 6, ""),
    _EntradaTpDoc(49, 70, ""),
    _EntradaTpDoc(50, 38, ""),
    _EntradaTpDoc(51, 102, ""),
    _EntradaTpDoc(52, 22, ""),
    _EntradaTpDoc(53, 86, ""),
    _EntradaTpDoc(54, 54, ""),
    _EntradaTpDoc(55, 118, ""),
    _EntradaTpDoc(56, 14, ""),
    _EntradaTpDoc(57, 78, ""),
    _EntradaTpDoc(58, 46, ""),
    _EntradaTpDoc(59, 110, ""),
    _EntradaTpDoc(60, 30, ""),
    _EntradaTpDoc(61, 94, ""),
    _EntradaTpDoc(62, 62, ""),
    _EntradaTpDoc(63, 126, ""),
)

POR_CODIGO: dict[int, _EntradaTpDoc] = {entrada.codigo: entrada for entrada in ENTRADAS}
POR_REVERSO: dict[int, _EntradaTpDoc] = {entrada.reverso: entrada for entrada in ENTRADAS}
POR_NOME: dict[str, _EntradaTpDoc] = {entrada.nome: entrada for entrada in ENTRADAS if entrada.nome}

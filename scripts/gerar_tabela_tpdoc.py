#!/usr/bin/env python3
"""Gera `src/csk_dfe/_tabela_tpdoc.py` a partir de `references/domain/tab-tpdoc.csv`.

O CSV é a fonte da verdade; este script materializa o conteúdo dele como um
módulo Python literal, para que a biblioteca não precise de I/O em tempo de
execução. Rode novamente sempre que o CSV mudar:

    uv run python scripts/gerar_tabela_tpdoc.py
"""

from __future__ import annotations

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV_ORIGEM = RAIZ / "references" / "domain" / "tab-tpdoc.csv"
MODULO_DESTINO = RAIZ / "src" / "csk_dfe" / "_tabela_tpdoc.py"

TAMANHO_TABELA = 64
BITS = 7

CABECALHO = '''"""Tabela de tipos de documento fiscal do CSK-DFE.

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

'''


def reverter_bits(codigo: int, bits: int = BITS) -> int:
    resultado = 0
    for i in range(bits):
        if codigo & (1 << i):
            resultado |= 1 << (bits - 1 - i)
    return resultado


def ler_csv(caminho: Path) -> list[tuple[int, int, str]]:
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = [
            (int(linha["codigo"]), int(linha["reverso"]), linha["Tipo"].strip())
            for linha in leitor
        ]
    return linhas


def validar(linhas: list[tuple[int, int, str]]) -> None:
    codigos = [codigo for codigo, _, _ in linhas]

    if len(linhas) != TAMANHO_TABELA:
        raise ValueError(
            f"esperava {TAMANHO_TABELA} entradas no CSV, encontrou {len(linhas)}"
        )

    if sorted(codigos) != list(range(TAMANHO_TABELA)):
        raise ValueError(
            "os códigos do CSV devem cobrir exatamente 0 a 63, sem lacunas nem repetições"
        )

    for codigo, reverso, _ in linhas:
        calculado = reverter_bits(codigo)
        if calculado != reverso:
            raise ValueError(
                f"código {codigo}: reverso do CSV é {reverso}, mas o calculado é {calculado}"
            )


def gerar_modulo(linhas: list[tuple[int, int, str]]) -> str:
    linhas_ordenadas = sorted(linhas, key=lambda linha: linha[0])

    entradas = "\n".join(
        f'    _EntradaTpDoc({codigo}, {reverso}, "{nome}"),'
        for codigo, reverso, nome in linhas_ordenadas
    )

    corpo = f"""ENTRADAS: tuple[_EntradaTpDoc, ...] = (
{entradas}
)

POR_CODIGO: dict[int, _EntradaTpDoc] = {{entrada.codigo: entrada for entrada in ENTRADAS}}
POR_REVERSO: dict[int, _EntradaTpDoc] = {{entrada.reverso: entrada for entrada in ENTRADAS}}
POR_NOME: dict[str, _EntradaTpDoc] = {{entrada.nome: entrada for entrada in ENTRADAS if entrada.nome}}
"""

    return CABECALHO + corpo


def main() -> None:
    linhas = ler_csv(CSV_ORIGEM)
    validar(linhas)
    MODULO_DESTINO.write_text(gerar_modulo(linhas), encoding="utf-8")
    print(f"Gerado {MODULO_DESTINO.relative_to(RAIZ)} a partir de {CSV_ORIGEM.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

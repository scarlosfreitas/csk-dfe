"""Codificação e decodificação Base62 de largura fixa da chave CSK-DFE."""

from __future__ import annotations

from .excecoes import Base62InvalidoError

_ALFABETO = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_BASE = len(_ALFABETO)
_LARGURA = 11
_LIMITE_CHAVE = 2**63


def to_base62(csk: int) -> str:
    """Codifica `csk` em texto Base62 de exatamente 11 caracteres, com padding `'0'` à esquerda."""
    valor = csk
    digitos = []
    for _ in range(_LARGURA):
        valor, resto = divmod(valor, _BASE)
        digitos.append(_ALFABETO[resto])
    return "".join(reversed(digitos))


def from_base62(texto: str) -> int:
    """Decodifica um texto Base62 de 11 caracteres de volta à chave inteira que o originou."""
    if len(texto) != _LARGURA:
        raise Base62InvalidoError(
            f"texto Base62 {texto!r} não tem {_LARGURA} caracteres"
        )

    valor = 0
    for caractere in texto:
        indice = _ALFABETO.find(caractere)
        if indice == -1:
            raise Base62InvalidoError(
                f"caractere {caractere!r} fora do alfabeto Base62 {_ALFABETO!r}"
            )
        valor = valor * _BASE + indice

    if valor >= _LIMITE_CHAVE:
        raise Base62InvalidoError(
            f"valor decodificado {valor} não cabe em uma chave de 63 bits"
        )

    return valor

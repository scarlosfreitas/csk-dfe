"""Hash de segmentação do contribuinte a partir da raiz do CNPJ."""

from __future__ import annotations

from .excecoes import CnpjInvalidoError

_OFFSET_BASIS = 0x811C9DC5
_PRIMO = 0x01000193
_MASCARA_32_BITS = 0xFFFFFFFF
_TAMANHO_RAIZ = 8


def hash_cnpj(cnpj: str) -> int:
    """Segmenta o contribuinte em 0–63 a partir da raiz de 8 caracteres do CNPJ.

    Descarta todo caractere não alfanumérico e aplica o FNV-1a de 32 bits
    sobre os 8 primeiros caracteres restantes, reduzindo o resultado por
    `& 63`. Levanta `CnpjInvalidoError` se, após a normalização, sobrarem
    menos de 8 caracteres.
    """
    normalizado = "".join(caractere for caractere in cnpj if caractere.isalnum())
    if len(normalizado) < _TAMANHO_RAIZ:
        raise CnpjInvalidoError(
            f"CNPJ {cnpj!r} tem menos de {_TAMANHO_RAIZ} caracteres alfanuméricos"
        )

    raiz = normalizado[:_TAMANHO_RAIZ]
    hash_valor = _OFFSET_BASIS
    for caractere in raiz:
        hash_valor ^= ord(caractere)
        hash_valor = (hash_valor * _PRIMO) & _MASCARA_32_BITS

    return hash_valor & 63

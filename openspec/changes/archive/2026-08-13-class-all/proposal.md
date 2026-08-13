## Why

A change `class-tpdoc` entregou apenas o campo de documento da chave. Os outros três campos — data, segmento de CNPJ e o número de desambiguação — não existem, e sem eles a biblioteca não gera nem decodifica um CSK-DFE: `TpDoc` sozinho não serve a nenhum consumidor. Esta change fecha o §4 do PRD e torna a biblioteca utilizável pelo Catálogo 2.0 e pela `dfe-data-platform`.

## What Changes

- Novo `csk_dfe.hash_cnpj(cnpj)` — FNV-1a de 32 bits sobre a raiz de 8 caracteres, reduzido por `& 63`, aceitando raízes alfanuméricas e CNPJ completo.
- Novo `csk_dfe.generate(dhemi, tpdoc, cnpj)` — monta a chave de 64 bits a partir da data (`datetime`, `date` ou string `AAMMDD`), do `TpDoc` e do CNPJ, com os 30 bits menos significativos vindos de `random.getrandbits(30)`.
- Novo `csk_dfe.decode(csk)` — devolve uma NamedTuple `CskDecodificado` com `dhemi`, `tpdoc`, `hash_cnpj` e `random_number`, validando a chave em vez de apenas fatiar os bits.
- Novos `csk_dfe.to_base62(csk)` e `csk_dfe.from_base62(texto)` — representação textual de largura fixa, 11 caracteres, alfabeto `0-9A-Za-z`, com padding `'0'` à esquerda e ordenação lexicográfica coerente com a ordenação numérica da chave.
- Novas exceções de domínio para data inválida, CNPJ inválido, chave inválida e Base62 inválida, seguindo o padrão já estabelecido em `excecoes.py`.
- **Nomenclatura**: o campo de 30 bits passa a se chamar `random_number` em toda a spec, no código, nos testes e no notebook. O PRD e `references/domain/csk_dfe_components.md` o chamam de "aleatório" / "número aleatório"; esta change alinha os documentos ao novo nome. Não é uma mudança de comportamento.
- Novo `notebooks/csk-dfe.ipynb` — demonstração narrada da chave completa, com saídas legíveis e sem asserções. A autoridade sobre a correção continua sendo a suíte pytest.

## Capabilities

### New Capabilities

- `hash-cnpj`: segmentação do contribuinte em 64 faixas a partir da raiz de 8 caracteres do CNPJ, pelo FNV-1a normativo.
- `chave-composta`: composição e decomposição da chave de 64 bits — `generate()`, `decode()`, validação de data na janela 2000–2099, ordenação cronológica pela ordenação numérica e o campo `random_number`.
- `base62`: codificação e decodificação textual de largura fixa da chave.

### Modified Capabilities

Nenhuma. `tipo-documento` é consumida por `generate()` e `decode()` sem que nenhum de seus requisitos mude.

## Impact

- **Código**: novos módulos em `src/csk_dfe/`; `excecoes.py` ganha erros; `__init__.py` passa a exportar as cinco funções do §4 do PRD e `CskDecodificado`.
- **Documentação**: `specs/PRD.md` (§1.4, §4 e critérios 20–21 do §8) e `references/domain/csk_dfe_components.md` passam a usar `random_number` para nomear o campo de 30 bits.
- **Dependências**: nenhuma nova. Tudo vem da stdlib (`random`, `datetime`), mantendo o critério 27.
- **Compatibilidade**: aditiva. Nada do que `class-tpdoc` entregou muda de assinatura ou de comportamento.
- **Consumidores**: a partir desta change, Catálogo 2.0 e `dfe-data-platform` conseguem gerar e decodificar chaves. A unicidade continua sendo responsabilidade deles.

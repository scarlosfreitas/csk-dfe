## Why

Nem todo documento que precisa de um CSK-DFE traz um CNPJ utilizável no momento da geração da chave, e nem todo documento tem data de emissão. Hoje `generate()` exige `cnpj` e chama o primeiro parâmetro de `dhemi`, o que impede o primeiro caso e descreve mal o segundo: em um lote de DF-e, o que a chave carrega é a data de **recepção**, não a de emissão.

## What Changes

- **BREAKING** — `generate(dhemi, tpdoc, cnpj)` passa a ser `generate(data, tpdoc, cnpj=None)`. O primeiro parâmetro é renomeado de `dhemi` para `data`, sem alias nem período de depreciação.
- **BREAKING** — o campo `dhemi` de `CskDecodificado` é renomeado para `data`. A ordem posicional dos quatro campos não muda.
- `cnpj` torna-se opcional. Quando omitido (ou `None`), os 6 bits reservados ao hash do CNPJ recebem bits aleatórios do mesmo gerador que preenche o `random_number`, de modo que os 36 bits menos significativos da chave sejam integralmente aleatórios.
- A chave gerada sem CNPJ **não carrega marcador**: é indistinguível de uma chave com CNPJ. `decode()` permanece com os mesmos quatro campos e continua devolvendo `hash_cnpj` de `0` a `63`; quando a chave foi gerada sem CNPJ esse valor é ruído e não deve ser interpretado como segmento de contribuinte. Isso é documentado, não sinalizado na chave.
- O código de documento `31` (reverso `124`), hoje reservado, passa a nomear o tipo **`Lote DFe`** em `references/domain/tab-tpdoc.csv`, tornando-o resolvível por `TpDoc.from_cod(31)`, `from_reverse_cod(124)` e `from_name("Lote DFe")`.
- A semântica do campo de data é redefinida na documentação e nas specs: `data` é a data do documento — de emissão para documentos fiscais em geral, de recepção para lotes de DF-e. O termo `dhemi` é eliminado de specs, código, testes, PRD e notebooks.
- `specs/PRD.md` é atualizado: o §4 renomeia `dhemi` para `data` e marca `cnpj` como opcional; o §8 ganha critérios numerados novos para o modo sem CNPJ e para o tipo `Lote DFe`.
- Um notebook de demonstração narrada é acrescentado a `notebooks/`, exibindo o uso das funções com saídas legíveis. O notebook não contém asserções: a autoridade de teste é o `pytest`.

## Capabilities

### New Capabilities

Nenhuma. A mudança altera capacidades já existentes.

### Modified Capabilities

- `chave-composta`: `cnpj` passa a ser opcional em `generate()`; os 6 bits do hash recebem aleatório quando ele é omitido; o campo de data é renomeado de `dhemi` para `data` na entrada e na saída, com a semântica ampliada para data de recepção nos lotes de DF-e.
- `tipo-documento`: o código `31` deixa de ser reservado e passa a resolver para o tipo `Lote DFe`.

## Impact

- `references/domain/tab-tpdoc.csv` — fonte da verdade do domínio: a linha `31,124,` passa a `31,124,Lote DFe`.
- `specs/PRD.md` — §4 (assinaturas e parâmetros) e §8 (critérios de aceitação, que passam de 27 para um número maior).
- `openspec/config.yaml` — o bloco `context:` menciona o layout da chave e precisa registrar o modo sem CNPJ e o nome `data`.
- `src/csk_dfe/chave.py` — assinatura de `generate()`, campos de `CskDecodificado`, alias de tipo `DhEmi`, função `_normalizar_dhemi` e docstrings.
- `tests/test_chave.py` e `tests/test_tpdoc.py` — casos renomeados e casos novos para o modo sem CNPJ e para o código 31.
- `notebooks/` — notebook de demonstração narrada novo; o notebook histórico `csk-dfe.ipynb` menciona `dhemi`.
- Consumidores que chamem `generate(dhemi=...)` por palavra-chave ou leiam `resultado.dhemi` quebram. A biblioteca ainda não tem versão publicada, e a quebra foi aceita explicitamente.
- Sem impacto em `hash_cnpj()`, `to_base62()` e `from_base62()`, que permanecem inalterados.

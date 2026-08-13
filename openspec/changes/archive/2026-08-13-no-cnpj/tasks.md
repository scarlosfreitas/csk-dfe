## 1. Fonte da verdade do domínio

- [x] 1.1 Alterar a linha do código `31` em `references/domain/tab-tpdoc.csv` de `31,124,` para `31,124,Lote DFe`, sem mexer em nenhuma outra linha
- [x] 1.2 Rodar `scripts/gerar_tabela_tpdoc.py` e conferir que o único diff em `src/csk_dfe/_tabela_tpdoc.py` é `_EntradaTpDoc(31, 124, "")` → `_EntradaTpDoc(31, 124, "Lote DFe")`
- [x] 1.3 Revisar `references/domain/csk_dfe_components.md`: trocar qualquer menção a data de emissão pela definição de data do documento (emissão para documentos fiscais, recepção para lotes de DF-e) e registrar que o campo de 6 bits recebe aleatório quando não há CNPJ

## 2. PRD

- [x] 2.1 No §4 de `specs/PRD.md`, renomear o parâmetro `dhemi` de `generate()` para `data`, descrevê-lo como data do documento com a regra emissão/recepção, e marcar `cnpj` como opcional
- [x] 2.2 No §4, renomear o campo de retorno `dhemi` de `decode()` para `data` e acrescentar a ressalva de que `hash_cnpj` não é interpretável quando a chave foi gerada sem CNPJ
- [x] 2.3 No §8, ajustar os critérios 3 e 6 para falarem em data do documento em vez de data de emissão, sem renumerar nada
- [x] 2.4 No §8, acrescentar os critérios 28, 29 e 30 na redação fixada em `design.md — O PRD é emendado antes do código`
- [x] 2.5 Remover `Lote DFe` de `## 9. Evoluções futuras` caso apareça lá, e conferir que nenhuma outra seção do PRD ainda diz `dhemi`

## 3. Contexto do OpenSpec

- [x] 3.1 Atualizar o bloco `context:` de `openspec/config.yaml`: o campo de data passa a ser a data do documento, o campo de 6 bits recebe aleatório quando o CNPJ é omitido, e a contagem de critérios do §8 deixa de ser 27

## 4. Implementação

- [x] 4.1 Em `src/csk_dfe/chave.py`, renomear o alias de tipo `DhEmi` para `Data` e a função `_normalizar_dhemi` para `_normalizar_data`, ajustando as mensagens de erro que citam `dhemi`
- [x] 4.2 Renomear o campo `dhemi` de `CskDecodificado` para `data`, mantendo-o na primeira posição
- [x] 4.3 Mudar a assinatura para `generate(data: Data, tpdoc: TpDoc, cnpj: str | None = None) -> int`
- [x] 4.4 Implementar o ramo sem CNPJ: quando `cnpj is None`, somar `random.getrandbits(36)` aos 36 bits menos significativos em um único sorteio; quando informado, manter `hash_cnpj(cnpj) << 30` mais `getrandbits(30)`
- [x] 4.5 Garantir que `cnpj=""` continue sendo rejeitado por `hash_cnpj()` e não selecione o modo sem CNPJ
- [x] 4.6 Atualizar as docstrings de `generate()` e `decode()`: a semântica de `data`, o modo sem CNPJ, e o aviso de que `hash_cnpj` é ruído quando a chave foi gerada sem CNPJ
- [x] 4.7 Conferir que `src/csk_dfe/__init__.py` não precisa de mudança de exportações e que `TpDoc.from_name("Lote DFe")` resolve

## 5. Testes

- [x] 5.1 Renomear em `tests/test_chave.py` todo uso de `dhemi` para `data`, incluindo o acesso ao campo do resultado de `decode()`
- [x] 5.2 Cobrir o cenário `Chave gerada sem CNPJ`: campos de data e de tipo de documento intactos, chave positiva e dentro da faixa do dia
- [x] 5.3 Cobrir `Faixa dos 36 bits aleatórios` e `Chaves distintas sem CNPJ`, com `random` semeado ou monkeypatched para exercitar `0` e `2**36 - 1` sem transbordo para o campo de tipo de documento
- [x] 5.4 Cobrir `Decomposição de chave gerada sem CNPJ` e `Ida e volta sem CNPJ`
- [x] 5.5 Cobrir `Rejeição de datas inválidas` no modo sem CNPJ, verificando que o erro é o mesmo do modo com CNPJ
- [x] 5.6 Cobrir `Particionamento preservado sem CNPJ` e a ordenação cronológica entre 2022 e 2023 com chaves dos dois modos misturadas
- [x] 5.7 Cobrir em `tests/test_tpdoc.py` as três resoluções do `Lote DFe` (código `31`, reverso `124`, nome `Lote DFe`) e conferir que o teste de aderência ao CSV continua passando
- [x] 5.8 Cobrir o cenário `Data de recepção em lote de DF-e`: chave de `Lote DFe` com data de recepção 01/01/2022 tem campo de data `220101`
- [x] 5.9 Rodar a suíte completa e conferir que passa inteira

## 6. Notebook de demonstração

- [x] 6.1 Criar o notebook narrado em `notebooks/`, com células de markdown explicando o layout da chave e o papel de cada campo
- [x] 6.2 Demonstrar `generate()` com CNPJ e `decode()`, exibindo a chave em decimal, em binário segmentado por campo, em Base62 e o resultado decomposto em saída legível
- [x] 6.3 Demonstrar `generate()` sem CNPJ lado a lado, tornando visível que os 36 bits menos significativos são aleatórios e que `decode()` devolve os mesmos quatro campos
- [x] 6.4 Demonstrar o `Lote DFe` com data de recepção, e a consulta por faixa de datas sobre a chave
- [x] 6.5 Conferir que o notebook não contém nenhum `assert` nem verificação que possa falhar como teste, e que ele roda de ponta a ponta com o kernel limpo

## 7. Fechamento

- [x] 7.1 Buscar `dhemi` em todo o repositório e confirmar zero ocorrências fora de `openspec/changes/archive/`, incluindo `notebooks/csk-dfe.ipynb` e o `README`
- [x] 7.2 Rodar `openspec validate "no-cnpj" --strict`
- [x] 7.3 Conferir que cada cenário das specs desta change tem teste correspondente na suíte

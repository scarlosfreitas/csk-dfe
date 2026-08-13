## 1. Exceções de domínio

- [x] 1.1 Introduzir `CskDfeError`, derivada de `ValueError`, como base de todas as exceções do pacote, e fazer `TpDocError` derivar dela
- [x] 1.2 Definir `CnpjInvalidoError`, `DataInvalidaError`, `ChaveInvalidaError` e `Base62InvalidoError`
- [x] 1.3 Confirmar que os testes de `tipo-documento` continuam passando sem alteração

## 2. Hash do CNPJ

- [x] 2.1 Criar `src/csk_dfe/cnpj.py` com `hash_cnpj(cnpj)`
- [x] 2.2 Normalizar a entrada descartando todo caractere não alfanumérico
- [x] 2.3 Rejeitar com `CnpjInvalidoError` a entrada que, normalizada, tenha menos de 8 caracteres
- [x] 2.4 Implementar o FNV-1a de 32 bits sobre os 8 primeiros caracteres, com XOR do byte antes da multiplicação, offset basis `0x811C9DC5`, primo `0x01000193` e truncamento por `& 0xFFFFFFFF`
- [x] 2.5 Reduzir o resultado por `& 63`

## 3. Base62

- [x] 3.1 Criar `src/csk_dfe/base62.py` com o alfabeto `0-9A-Za-z` em ordem de ponto de código
- [x] 3.2 Implementar `to_base62(csk)` devolvendo sempre 11 caracteres, com padding `'0'` à esquerda
- [x] 3.3 Implementar `from_base62(texto)`, rejeitando comprimento diferente de 11, caractere fora do alfabeto e valor maior ou igual a `2**63`, com `Base62InvalidoError`

## 4. Composição e decomposição da chave

- [x] 4.1 Criar `src/csk_dfe/chave.py` com as constantes de deslocamento e largura dos quatro campos
- [x] 4.2 Implementar a normalização de `dhemi`, aceitando `datetime` (descartando a hora), `date` e string de 6 dígitos `AAMMDD`
- [x] 4.3 Rejeitar com `DataInvalidaError` datas fora do calendário e fora da janela 2000–2099, reembalando o erro de `datetime.date`
- [x] 4.4 Implementar `generate(dhemi, tpdoc, cnpj)` compondo `AAMMDD * 2**43 + reverso * 2**36 + segmento * 2**30 + random_number`, com `random_number = random.getrandbits(30)`
- [x] 4.5 Definir `CskDecodificado` como `NamedTuple` com `dhemi`, `tpdoc`, `hash_cnpj` e `random_number`, nessa ordem
- [x] 4.6 Implementar `decode(csk)` fatiando os quatro campos e devolvendo `CskDecodificado`
- [x] 4.7 Em `decode()`, rejeitar com `ChaveInvalidaError` valor negativo, valor maior ou igual a `2**63` e campo de data sem correspondência no calendário
- [x] 4.8 Confirmar que `decode()` propaga o erro de tabela estendida vindo de `TpDoc.from_reverse_cod()` para reverso ímpar

## 5. API pública

- [x] 5.1 Reexportar em `__init__.py` as cinco funções do §4 do PRD, `CskDecodificado` e as novas exceções
- [x] 5.2 Atualizar `__all__` e escrever docstrings em português, registrando que a hora de `dhemi` é descartada e que o CNPJ não é recuperável

## 6. Testes de hash do CNPJ

- [x] 6.1 Testar os vetores do critério 16: `"11111111"→13`, `"22222222"→5`, `"99999999"→29`, `"ABCDEFGH"→13`, `"1111111A"→61`
- [x] 6.2 Testar que o segmento está sempre na faixa 0–63 para um conjunto amplo de raízes
- [x] 6.3 Testar que CNPJ completo, raiz e outra filial do mesmo contribuinte produzem o mesmo segmento
- [x] 6.4 Testar que CNPJ formatado com pontos, barra e traço produz o mesmo segmento do não formatado
- [x] 6.5 Testar que raiz alfanumérica é aceita e que a caixa do caractere altera o segmento
- [x] 6.6 Testar a rejeição de entrada vazia e de entrada com menos de 8 caracteres alfanuméricos

## 7. Testes da chave

- [x] 7.1 Testar a identidade aritmética da chave a partir dos quatro campos decompostos
- [x] 7.2 Testar que o bit 63 é sempre `0`
- [x] 7.3 Testar que o campo de 7 bits contém o código reverso, e não o direto
- [x] 7.4 Testar que `date`, `datetime` e a string `AAMMDD` do mesmo dia produzem o mesmo campo de data
- [x] 7.5 Testar a faixa do critério 4: chave de 01/01/2022 entre `220101 * 2**43` e `220102 * 2**43`
- [x] 7.6 Testar a ordenação cronológica do critério 5 entre chaves de 2022 e de 2023
- [x] 7.7 Testar a rejeição de `991331`, `220230` e `000000`, e de string fora do formato de 6 dígitos
- [x] 7.8 Testar a rejeição de datas anteriores a 2000 e posteriores a 2099
- [x] 7.9 Testar a ida e volta de `generate()` para `decode()` em data, tipo de documento e segmento
- [x] 7.10 Testar que `decode()` de uma chave com campo de data `220101` devolve 01/01/2022
- [x] 7.11 Testar que duas chamadas consecutivas de `generate()` com os mesmos argumentos produzem chaves diferentes
- [x] 7.12 Testar os extremos de `random_number` (`0` e `2**30 - 1`) com `monkeypatch` sobre `csk_dfe.chave.random.getrandbits`, confirmando que não há transbordo para o campo de segmento
- [x] 7.13 Testar que várias chaves consecutivas não formam progressão no campo `random_number`
- [x] 7.14 Testar a rejeição em `decode()` de valor negativo, de valor maior ou igual a `2**63` e de campo de data inválido
- [x] 7.15 Testar que `decode()` rejeita chave com campo de documento de tabela estendida
- [x] 7.16 Testar que `CskDecodificado` é desempacotável posicionalmente na ordem do §4 do PRD
- [x] 7.17 Testar que `generate()` e `decode()` não abrem nenhum arquivo
- [x] 7.18 Testar que o pacote importa e gera chaves em ambiente com apenas a stdlib

## 8. Testes de Base62

- [x] 8.1 Testar que `to_base62()` devolve 11 caracteres do alfabeto para chaves de magnitudes variadas
- [x] 8.2 Testar o padding do critério 22: `to_base62(101 * 2**43)` começa com dois `'0'`
- [x] 8.3 Testar que `to_base62(0)` devolve 11 caracteres `'0'`
- [x] 8.4 Testar a ordenação lexicográfica do critério 23 sobre um conjunto variado de chaves ordenadas
- [x] 8.5 Testar a ida e volta `from_base62(to_base62(k)) == k`, incluindo `0` e `2**63 - 1`
- [x] 8.6 Testar a rejeição de comprimento diferente de 11, de caractere fora do alfabeto, de texto vazio e de valor maior ou igual a `2**63`

## 9. Notebook de demonstração

- [x] 9.1 Criar `notebooks/csk-dfe.ipynb` importando `csk_dfe` do ambiente do projeto, com narrativa em português e referência a `notebooks/tpdoc.ipynb` para a reversão de bits
- [x] 9.2 Exibir a chave montada campo a campo, com o binário de 64 bits anotado e os quatro campos alinhados sob os seus deslocamentos
- [x] 9.3 Demonstrar `generate()` nas três formas de `dhemi`, mostrando que a hora é descartada
- [x] 9.4 Demonstrar `decode()` exibindo `CskDecodificado` com os campos nomeados, e evidenciar que o CNPJ não volta
- [x] 9.5 Demonstrar a faixa SQL de um período, com os limites `220101 * 2**43` e `230801 * 2**43` calculados e exibidos
- [x] 9.6 Demonstrar `hash_cnpj()` agrupando filiais do mesmo contribuinte no mesmo segmento, e mostrar a distribuição dos segmentos para um lote de raízes
- [x] 9.7 Demonstrar que duas chamadas iguais de `generate()` dão chaves diferentes, e comentar a ordem de grandeza de 2³⁰ por combinação de dia, tipo e segmento
- [x] 9.8 Demonstrar `to_base62()` e `from_base62()`, exibindo chaves ordenadas lado a lado com seus textos para evidenciar que a ordem se preserva
- [x] 9.9 Demonstrar os erros de domínio: data inválida, CNPJ curto, chave inválida e Base62 inválido
- [x] 9.10 Manter o notebook sem asserções — a verificação é da suíte pytest

## 10. Alinhamento da documentação

- [x] 10.1 Renomear para `random_number` as menções ao campo de 30 bits em `specs/PRD.md` (§1.4, §4 e critérios 20–21 do §8)
- [x] 10.2 Renomear para `random_number` a menção ao campo em `references/domain/csk_dfe_components.md`
- [x] 10.3 Atualizar o bloco `context:` de `openspec/config.yaml` com o novo nome do campo
- [x] 10.4 Atualizar `CLAUDE.md` removendo a afirmação de que não existe código Python e registrando o nome `random_number`

## 11. Fechamento

- [x] 11.1 Executar a suíte completa e confirmar que todos os cenários das specs `hash-cnpj`, `chave-composta` e `base62` estão cobertos
- [x] 11.2 Executar o notebook do início ao fim e versioná-lo com as saídas
- [x] 11.3 Confirmar que nenhuma afirmação do código, dos testes ou do notebook contradiz `references/domain/csk_dfe_components.md` ou o §8 do PRD
- [x] 11.4 Rodar `openspec validate "class-all" --strict`

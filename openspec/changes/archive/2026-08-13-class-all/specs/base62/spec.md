## Purpose

Representar a chave de 64 bits como texto curto de largura fixa, para uso em URL, nome de arquivo e chave de objeto, preservando na ordenação alfabética a mesma ordem que a chave tem na ordenação numérica.

## ADDED Requirements

### Requirement: Largura fixa de 11 caracteres

O sistema SHALL codificar qualquer chave válida como exatamente 11 caracteres do alfabeto `0-9A-Za-z`, completando com `'0'` à esquerda quando a chave tiver menos dígitos significativos.

Rastreia o critério 22 do §8 do PRD.

#### Scenario: Chave de magnitude comum

- **WHEN** uma chave gerada é codificada
- **THEN** o texto obtido tem exatamente 11 caracteres, todos dentro do alfabeto `0-9A-Za-z`

#### Scenario: Chave de baixa magnitude recebe padding

- **WHEN** a chave `101 * 2**43`, que tem 9 dígitos significativos na base 62, é codificada
- **THEN** o texto obtido tem 11 caracteres, sendo os dois primeiros `'0'`

#### Scenario: Chave zero

- **WHEN** o valor `0` é codificado
- **THEN** o texto obtido é composto por 11 caracteres `'0'`

### Requirement: Ordenação preservada

A ordenação lexicográfica dos textos codificados SHALL corresponder à ordenação numérica das chaves que os originaram — é o que permite ordenar e fazer faixa sobre o texto sem decodificar.

Rastreia o critério 23 do §8 do PRD.

#### Scenario: Ordem entre duas chaves

- **WHEN** duas chaves `a` e `b` com `a < b` são codificadas
- **THEN** o texto de `a` é lexicograficamente menor que o texto de `b`

#### Scenario: Ordem preservada em um conjunto

- **WHEN** um conjunto variado de chaves é codificado e os textos são ordenados alfabeticamente
- **THEN** a ordem dos textos coincide com a ordem numérica das chaves correspondentes

### Requirement: Ida e volta

O sistema SHALL decodificar um texto que ele mesmo produziu de volta à chave original, sem perda.

Rastreia o critério 24 do §8 do PRD.

#### Scenario: Decodificação devolve a chave

- **WHEN** uma chave é codificada e o texto resultante é decodificado
- **THEN** o valor obtido é igual à chave original

#### Scenario: Ida e volta nos extremos

- **WHEN** os valores `0` e `2**63 - 1`, extremos da faixa da chave, são codificados e decodificados
- **THEN** os valores obtidos são iguais aos originais

### Requirement: Rejeição de texto inválido

O sistema SHALL rejeitar com erro explícito o texto cujo comprimento seja diferente de 11, que contenha qualquer caractere fora do alfabeto `0-9A-Za-z`, ou cujo valor decodificado não caiba na faixa de uma chave.

Rastreia o critério 25 do §8 do PRD.

#### Scenario: Comprimento diferente de 11

- **WHEN** um texto com menos ou mais de 11 caracteres é decodificado
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Caractere fora do alfabeto

- **WHEN** um texto de 11 caracteres contendo um caractere fora de `0-9A-Za-z` é decodificado
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Texto vazio

- **WHEN** um texto vazio é decodificado
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Texto cujo valor excede a faixa da chave

- **WHEN** um texto de 11 caracteres válidos cujo valor é maior ou igual a `2**63` é decodificado
- **THEN** o sistema rejeita a operação com erro explícito

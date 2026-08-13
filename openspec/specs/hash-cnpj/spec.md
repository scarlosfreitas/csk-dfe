# hash-cnpj Specification

## Purpose

Segmentar o contribuinte em 64 faixas a partir da raiz do seu CNPJ, para que documentos de um mesmo contribuinte fiquem agrupados dentro da partição do dia. O segmento é derivado por um hash não criptográfico e não permite recuperar o CNPJ.

## Requirements

### Requirement: Segmentação pelo hash normativo

O sistema SHALL derivar o segmento do contribuinte aplicando o algoritmo definido em `references/domain/csk_dfe_components.md` — FNV-1a de 32 bits, com XOR do byte antes da multiplicação — sobre a raiz de 8 caracteres, reduzindo o resultado por `& 63`.

Rastreia o critério 16 do §8 do PRD.

#### Scenario: Vetores normativos do hash

- **WHEN** o segmento é calculado para as raízes `11111111`, `22222222`, `99999999`, `ABCDEFGH` e `1111111A`
- **THEN** os segmentos obtidos são, respectivamente, `13`, `5`, `29`, `13` e `61`

#### Scenario: Sensibilidade a um único caractere

- **WHEN** o segmento é calculado para `11111111` e para `1111111A`, que diferem em um caractere
- **THEN** os segmentos obtidos são diferentes entre si

### Requirement: Faixa do segmento

O segmento produzido SHALL estar sempre na faixa de `0` a `63`, cabendo nos 6 bits reservados ao campo de CNPJ base da chave.

Rastreia o critério 17 do §8 do PRD.

#### Scenario: Segmento sempre representável em 6 bits

- **WHEN** o segmento é calculado para um conjunto amplo e variado de raízes válidas
- **THEN** todo segmento obtido está entre `0` e `63`, inclusive

### Requirement: Escopo da raiz de 8 caracteres

O sistema SHALL considerar apenas os 8 primeiros caracteres da entrada normalizada, de modo que o CNPJ completo e a sua raiz produzam o mesmo segmento — é o que faz filiais de um mesmo contribuinte caírem na mesma faixa.

Rastreia o critério 18 do §8 do PRD.

#### Scenario: CNPJ completo e raiz coincidem

- **WHEN** o segmento é calculado para um CNPJ completo de 14 caracteres e para os seus 8 primeiros caracteres
- **THEN** os dois segmentos são iguais

#### Scenario: Filiais do mesmo contribuinte

- **WHEN** o segmento é calculado para dois CNPJ que compartilham a raiz e diferem apenas no sufixo de filial
- **THEN** os dois segmentos são iguais

### Requirement: Raízes alfanuméricas

O sistema SHALL aceitar raízes de CNPJ alfanuméricas, tratando cada caractere pelo seu byte, sem exigir que a entrada seja numérica.

Rastreia o critério 19 do §8 do PRD.

#### Scenario: Raiz alfanumérica

- **WHEN** o segmento é calculado para a raiz `ABCDEFGH`
- **THEN** o segmento é produzido normalmente, sem erro

#### Scenario: Caixa do caractere é significativa

- **WHEN** o segmento é calculado para `ABCDEFGH` e para `ABCDEFGh`
- **THEN** os segmentos obtidos são diferentes, porque os bytes de entrada diferem

> Nota: a sensibilidade à caixa não garante segmentos diferentes para todo par — com apenas 64 segmentos, duas raízes distintas podem colidir por acaso após a redução `& 63`. É o caso de `ABCDEFGH` e `abcdefgh`, que colidem no segmento 13 apesar de terem hashes de 32 bits completos diferentes.

### Requirement: Normalização e rejeição de entrada insuficiente

O sistema SHALL descartar da entrada todo caractere que não seja alfanumérico antes de extrair a raiz, e SHALL rejeitar com erro explícito a entrada que, já normalizada, tenha menos de 8 caracteres.

#### Scenario: CNPJ formatado

- **WHEN** o segmento é calculado para um CNPJ escrito com pontos, barra e traço
- **THEN** o segmento obtido é igual ao do mesmo CNPJ escrito sem separadores

#### Scenario: Entrada curta demais

- **WHEN** o segmento é calculado para uma entrada que, sem os caracteres não alfanuméricos, tem menos de 8 caracteres
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Entrada vazia

- **WHEN** o segmento é calculado para uma string vazia
- **THEN** o sistema rejeita a operação com erro explícito

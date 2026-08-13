## ADDED Requirements

### Requirement: Geração sem CNPJ

O sistema SHALL permitir a geração da chave sem que um CNPJ seja informado. Nesse caso, os 6 bits reservados ao hash do CNPJ SHALL receber bits do mesmo gerador não criptográfico que preenche o número de desambiguação, de modo que os 36 bits menos significativos da chave sejam integralmente aleatórios.

Rastreia o critério 28 do §8 do PRD.

#### Scenario: Chave gerada sem CNPJ

- **WHEN** uma chave é gerada informando apenas a data e o tipo de documento, sem CNPJ
- **THEN** a chave é composta com sucesso, com os campos de data e de tipo de documento inalterados
- **AND** os 36 bits menos significativos são aleatórios

#### Scenario: Faixa dos 36 bits aleatórios

- **WHEN** chaves são geradas sem CNPJ
- **THEN** os 36 bits menos significativos cobrem toda a faixa de `0` a `2**36 - 1`, sem transbordar para o campo de tipo de documento

#### Scenario: Chaves distintas sem CNPJ

- **WHEN** duas chaves são geradas em sequência com a mesma data e o mesmo tipo de documento, ambas sem CNPJ
- **THEN** as duas chaves são diferentes entre si

#### Scenario: Particionamento preservado sem CNPJ

- **WHEN** uma chave é gerada sem CNPJ para 01/01/2022
- **THEN** a chave é maior ou igual a `220101 * 2**43` e menor que `220102 * 2**43`

### Requirement: Ausência de marcador de origem do campo de CNPJ

A chave SHALL NOT registrar se foi gerada com ou sem CNPJ: uma chave gerada sem CNPJ é indistinguível de uma gerada com CNPJ. Na decomposição, o campo de segmento SHALL continuar sendo devolvido como inteiro de `0` a `63`, e o sistema SHALL NOT afirmar que esse valor identifica um contribuinte.

Rastreia o critério 29 do §8 do PRD.

#### Scenario: Decomposição de chave gerada sem CNPJ

- **WHEN** uma chave gerada sem CNPJ é decomposta
- **THEN** a decomposição é bem-sucedida e devolve os mesmos quatro campos de qualquer outra chave
- **AND** o campo de segmento do CNPJ traz um valor de `0` a `63` que não corresponde a nenhum contribuinte

#### Scenario: Nenhum campo distingue as duas origens

- **WHEN** uma chave gerada com CNPJ e uma chave gerada sem CNPJ são decompostas
- **THEN** nenhum campo do resultado permite determinar qual delas foi gerada sem CNPJ

## RENAMED Requirements

- FROM: `### Requirement: Formas aceitas de data de emissão`
- TO: `### Requirement: Formas aceitas da data do documento`

## MODIFIED Requirements

### Requirement: Composição da chave

O sistema SHALL compor a chave a partir da data do documento, do tipo de documento e, opcionalmente, do CNPJ, de modo que ela seja exatamente `AAMMDD * 2**43 + reverso * 2**36 + segmento * 2**30 + random_number`, onde `reverso` é o código reverso do tipo de documento e `segmento` é o hash da raiz do CNPJ quando ele é informado, ou um valor aleatório quando não é.

A data do documento SHALL ser a data de emissão para documentos fiscais em geral, e a data de recepção para lotes de DF-e. Documentos sem data de emissão SHALL usar a data que os identifique cronologicamente no seu próprio ciclo de vida.

Rastreia os critérios 1, 2 e 9 do §8 do PRD.

#### Scenario: Identidade aritmética da chave

- **WHEN** uma chave é gerada e decomposta em seus quatro campos
- **THEN** a chave é igual à soma dos campos multiplicados por `2**43`, `2**36`, `2**30` e `1`, respectivamente

#### Scenario: Chave sempre positiva

- **WHEN** uma chave é gerada para qualquer entrada válida, com ou sem CNPJ
- **THEN** o bit 63 da chave é `0` e a chave é representável como `BIGINT` positivo

#### Scenario: O campo de documento grava o código reverso

- **WHEN** uma chave é gerada para um tipo de documento cujo código é `5` e cujo código reverso é `80`
- **THEN** o campo de 7 bits da chave contém `80`, e não `5`

#### Scenario: Data de recepção em lote de DF-e

- **WHEN** uma chave é gerada para um lote de DF-e recebido em 01/01/2022
- **THEN** o campo de data contém `220101`, a data de recepção do lote

### Requirement: Formas aceitas da data do documento

O sistema SHALL aceitar a data do documento como data, como data e hora, ou como string no formato `AAMMDD`, produzindo a mesma chave para as três formas quando elas designam o mesmo dia. A hora, quando presente, SHALL ser descartada.

#### Scenario: Três formas do mesmo dia

- **WHEN** chaves são geradas para 01/01/2022 informado como data, como data e hora, e como a string `220101`
- **THEN** as três chaves têm o mesmo campo de data

#### Scenario: String fora do formato

- **WHEN** a data do documento é informada como string que não tenha exatamente 6 dígitos
- **THEN** o sistema rejeita a operação com erro explícito

### Requirement: Particionamento e ordenação por data

O campo de data SHALL ser o decimal literal `AAMMDD`, sem epoch, de modo que a ordenação numérica da chave reproduza a ordenação cronológica e que um período seja consultável como faixa contínua de valores.

Rastreia os critérios 4 e 5 do §8 do PRD.

#### Scenario: Faixa de um dia

- **WHEN** uma chave é gerada para 01/01/2022
- **THEN** a chave é maior ou igual a `220101 * 2**43` e menor que `220102 * 2**43`

#### Scenario: Ordenação cronológica entre anos

- **WHEN** chaves são geradas para documentos cuja data é de 2022 e de 2023, com quaisquer tipos de documento, com ou sem CNPJ
- **THEN** toda chave de 2022 é numericamente menor que toda chave de 2023

### Requirement: Rejeição de datas inválidas

O sistema SHALL rejeitar com erro explícito qualquer data que não corresponda a um dia real do calendário, mesmo quando o valor seja representável nos 20 bits do campo, e SHALL rejeitar datas fora da janela de século 2000–2099.

Rastreia os critérios 7 e 8 do §8 do PRD.

#### Scenario: Valores representáveis mas inexistentes no calendário

- **WHEN** a data do documento informada é `991331`, `220230` ou `000000`
- **THEN** o sistema rejeita a operação com erro explícito em cada caso

#### Scenario: Data anterior à janela de século

- **WHEN** a data do documento informada é de um ano anterior a 2000
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Data posterior à janela de século

- **WHEN** a data do documento informada é de um ano posterior a 2099
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Rejeição independe do CNPJ

- **WHEN** uma data inválida é informada em uma geração sem CNPJ
- **THEN** o sistema rejeita a operação com o mesmo erro explícito da geração com CNPJ

### Requirement: Decomposição da chave

O sistema SHALL decompor uma chave válida devolvendo, sob nomes próprios, a data do documento como data do calendário, o tipo de documento, o segmento do CNPJ e o `random_number`. O campo de data SHALL ser exposto sob o nome `data`. O resultado SHALL também ser desempacotável posicionalmente nessa ordem.

Rastreia os critérios 3 e 6 do §8 do PRD.

#### Scenario: Ida e volta

- **WHEN** uma chave é gerada a partir de uma data, um tipo de documento e um CNPJ, e em seguida decomposta
- **THEN** a data, o tipo de documento e o segmento do CNPJ devolvidos são iguais aos que originaram a chave

#### Scenario: Ida e volta sem CNPJ

- **WHEN** uma chave é gerada sem CNPJ e em seguida decomposta
- **THEN** a data e o tipo de documento devolvidos são iguais aos que originaram a chave

#### Scenario: Janela de século na leitura

- **WHEN** uma chave cujo campo de data vale `220101` é decomposta
- **THEN** a data devolvida é 01/01/2022

#### Scenario: O CNPJ não é devolvido

- **WHEN** uma chave é decomposta
- **THEN** o resultado traz o segmento de `0` a `63`, e em nenhum campo o CNPJ que originou a chave

### Requirement: Número de desambiguação

Os 30 bits menos significativos SHALL receber um `random_number` de gerador uniformemente distribuído e não criptográfico, cobrindo toda a faixa de `0` a `2**30 - 1`. Quando o CNPJ não é informado, o mesmo gerador SHALL alimentar também os 6 bits do campo de segmento. O sistema SHALL NOT usar sequência ou contador, e SHALL NOT garantir unicidade da chave, com ou sem CNPJ.

Rastreia os critérios 20 e 21 do §8 do PRD.

#### Scenario: Chaves distintas para os mesmos argumentos

- **WHEN** duas chaves são geradas em sequência com a mesma data, o mesmo tipo de documento e o mesmo CNPJ
- **THEN** as duas chaves são diferentes entre si

#### Scenario: Extremos da faixa do random_number

- **WHEN** o gerador produz o menor e o maior valor possíveis
- **THEN** a chave acomoda `0` e `2**30 - 1` no campo, sem transbordar para o campo de segmento de CNPJ

#### Scenario: Ausência de sequência

- **WHEN** várias chaves são geradas em sequência com os mesmos argumentos
- **THEN** os valores de `random_number` obtidos não formam uma progressão

### Requirement: Custo constante e ausência de I/O

A geração da chave SHALL executar em tempo constante em relação ao volume de chaves já geradas, SHALL NOT realizar I/O, e SHALL NOT depender de estado compartilhado entre processos, com ou sem CNPJ informado.

Rastreia os critérios 26 e 27 do §8 do PRD.

#### Scenario: Geração sem acesso a disco

- **WHEN** uma chave é gerada ou decomposta
- **THEN** nenhum arquivo é aberto durante a operação

#### Scenario: Independência do histórico

- **WHEN** uma chave é gerada depois de muitas outras terem sido geradas no mesmo processo
- **THEN** o resultado não depende de quantas chaves já foram geradas

#### Scenario: Somente biblioteca padrão

- **WHEN** o pacote é importado em um ambiente que contém apenas a biblioteca padrão do Python
- **THEN** a importação é bem-sucedida e as chaves são geradas normalmente

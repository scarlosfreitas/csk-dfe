## Purpose

Compor e decompor o CSK-DFE, o identificador de partição de 64 bits que reúne data de emissão, tipo de documento, segmento do contribuinte e um número de desambiguação em um único inteiro positivo, ordenável cronologicamente e consultável por faixa em SQL.

## ADDED Requirements

### Requirement: Composição da chave

O sistema SHALL compor a chave a partir da data de emissão, do tipo de documento e do CNPJ, de modo que ela seja exatamente `AAMMDD * 2**43 + reverso * 2**36 + segmento * 2**30 + random_number`, onde `reverso` é o código reverso do tipo de documento e `segmento` é o hash da raiz do CNPJ.

Rastreia os critérios 1, 2 e 9 do §8 do PRD.

#### Scenario: Identidade aritmética da chave

- **WHEN** uma chave é gerada e decomposta em seus quatro campos
- **THEN** a chave é igual à soma dos campos multiplicados por `2**43`, `2**36`, `2**30` e `1`, respectivamente

#### Scenario: Chave sempre positiva

- **WHEN** uma chave é gerada para qualquer entrada válida
- **THEN** o bit 63 da chave é `0` e a chave é representável como `BIGINT` positivo

#### Scenario: O campo de documento grava o código reverso

- **WHEN** uma chave é gerada para um tipo de documento cujo código é `5` e cujo código reverso é `80`
- **THEN** o campo de 7 bits da chave contém `80`, e não `5`

### Requirement: Formas aceitas de data de emissão

O sistema SHALL aceitar a data de emissão como data, como data e hora, ou como string no formato `AAMMDD`, produzindo a mesma chave para as três formas quando elas designam o mesmo dia. A hora, quando presente, SHALL ser descartada.

#### Scenario: Três formas do mesmo dia

- **WHEN** chaves são geradas para 01/01/2022 informado como data, como data e hora, e como a string `220101`
- **THEN** as três chaves têm o mesmo campo de data

#### Scenario: String fora do formato

- **WHEN** a data de emissão é informada como string que não tenha exatamente 6 dígitos
- **THEN** o sistema rejeita a operação com erro explícito

### Requirement: Particionamento e ordenação por data

O campo de data SHALL ser o decimal literal `AAMMDD`, sem epoch, de modo que a ordenação numérica da chave reproduza a ordenação cronológica e que um período seja consultável como faixa contínua de valores.

Rastreia os critérios 4 e 5 do §8 do PRD.

#### Scenario: Faixa de um dia

- **WHEN** uma chave é gerada para 01/01/2022
- **THEN** a chave é maior ou igual a `220101 * 2**43` e menor que `220102 * 2**43`

#### Scenario: Ordenação cronológica entre anos

- **WHEN** chaves são geradas para documentos emitidos em 2022 e em 2023, com quaisquer tipos de documento e CNPJ
- **THEN** toda chave de 2022 é numericamente menor que toda chave de 2023

### Requirement: Rejeição de datas inválidas

O sistema SHALL rejeitar com erro explícito qualquer data que não corresponda a um dia real do calendário, mesmo quando o valor seja representável nos 20 bits do campo, e SHALL rejeitar datas fora da janela de século 2000–2099.

Rastreia os critérios 7 e 8 do §8 do PRD.

#### Scenario: Valores representáveis mas inexistentes no calendário

- **WHEN** a data de emissão informada é `991331`, `220230` ou `000000`
- **THEN** o sistema rejeita a operação com erro explícito em cada caso

#### Scenario: Data anterior à janela de século

- **WHEN** a data de emissão informada é de um ano anterior a 2000
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Data posterior à janela de século

- **WHEN** a data de emissão informada é de um ano posterior a 2099
- **THEN** o sistema rejeita a operação com erro explícito

### Requirement: Decomposição da chave

O sistema SHALL decompor uma chave válida devolvendo, sob nomes próprios, a data de emissão como data do calendário, o tipo de documento, o segmento do CNPJ e o `random_number`. O resultado SHALL também ser desempacotável posicionalmente nessa ordem.

Rastreia os critérios 3 e 6 do §8 do PRD.

#### Scenario: Ida e volta

- **WHEN** uma chave é gerada a partir de uma data, um tipo de documento e um CNPJ, e em seguida decomposta
- **THEN** a data, o tipo de documento e o segmento do CNPJ devolvidos são iguais aos que originaram a chave

#### Scenario: Janela de século na leitura

- **WHEN** uma chave cujo campo de data vale `220101` é decomposta
- **THEN** a data devolvida é 01/01/2022

#### Scenario: O CNPJ não é devolvido

- **WHEN** uma chave é decomposta
- **THEN** o resultado traz o segmento de `0` a `63`, e em nenhum campo o CNPJ que originou a chave

### Requirement: Validação na decomposição

O sistema SHALL rejeitar com erro explícito a decomposição de um valor que não seja uma chave válida, em vez de devolver campos sem sentido.

#### Scenario: Valor negativo

- **WHEN** um valor negativo é decomposto
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Valor com o bit de sinal ocupado

- **WHEN** um valor maior ou igual a `2**63` é decomposto
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Campo de data sem correspondência no calendário

- **WHEN** um valor cujo campo de data é `991331` é decomposto
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Campo de documento de tabela estendida

- **WHEN** um valor cujo campo de documento tem o bit mais à direita igual a `1` é decomposto
- **THEN** o sistema rejeita a operação com erro explícito, informando que se trata de tabela estendida

### Requirement: Número de desambiguação

Os 30 bits menos significativos SHALL receber um `random_number` de gerador uniformemente distribuído e não criptográfico, cobrindo toda a faixa de `0` a `2**30 - 1`. O sistema SHALL NOT usar sequência ou contador, e SHALL NOT garantir unicidade da chave.

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

A geração da chave SHALL executar em tempo constante em relação ao volume de chaves já geradas, SHALL NOT realizar I/O, e SHALL NOT depender de estado compartilhado entre processos.

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

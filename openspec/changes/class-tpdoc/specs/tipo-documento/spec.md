## Purpose

Resolver tipos de documento fiscal do CSK-DFE nas três formas em que eles circulam: o nome legível, o código de domínio de 0 a 63, e o código reverso de 7 bits que é o valor efetivamente gravado no campo de documento da chave.

## ADDED Requirements

### Requirement: Resolução por código

O sistema SHALL resolver um tipo de documento a partir do seu código de domínio, aceitando apenas a faixa de 0 a 63.

#### Scenario: Código válido da tabela base

- **WHEN** um tipo de documento é resolvido pelo código `0`
- **THEN** o tipo resolvido tem código `0`, código reverso `0` e nome `NFe`

#### Scenario: Código válido sem nome atribuído

- **WHEN** um tipo de documento é resolvido pelo código `2`, que é reservado
- **THEN** o tipo é resolvido com sucesso, com código `2` e código reverso `32`
- **AND** o nome é vazio

#### Scenario: Código fora da faixa

- **WHEN** um tipo de documento é resolvido por um código menor que `0` ou maior que `63`
- **THEN** o sistema rejeita a operação com erro explícito

### Requirement: Resolução por código reverso

O sistema SHALL resolver um tipo de documento a partir do código reverso, que é a forma como o tipo aparece gravado na chave.

#### Scenario: Código reverso conhecido

- **WHEN** um tipo de documento é resolvido pelo código reverso `80`
- **THEN** o tipo resolvido tem código `5` e nome `NFCe`

#### Scenario: Código reverso ímpar, de tabela estendida

- **WHEN** um tipo de documento é resolvido por um código reverso ímpar, cujo bit mais à direita é `1`
- **THEN** o sistema rejeita a operação com erro explícito, informando que se trata de tabela estendida

#### Scenario: Código reverso fora de 7 bits

- **WHEN** um tipo de documento é resolvido por um código reverso menor que `0` ou maior que `127`
- **THEN** o sistema rejeita a operação com erro explícito

### Requirement: Resolução por nome

O sistema SHALL resolver um tipo de documento a partir do seu nome, e SHALL rejeitar nomes que não estejam atribuídos a nenhum código.

#### Scenario: Nome atribuído

- **WHEN** um tipo de documento é resolvido pelo nome `MDFe`
- **THEN** o tipo resolvido tem código `15` e código reverso `120`

#### Scenario: Nome inexistente

- **WHEN** um tipo de documento é resolvido por um nome que não consta da tabela
- **THEN** o sistema rejeita a operação com erro explícito

#### Scenario: Código reservado não é resolvível por nome

- **WHEN** um tipo de documento é resolvido pelo nome vazio
- **THEN** o sistema rejeita a operação com erro explícito, mesmo havendo códigos reservados sem nome na tabela

### Requirement: Regra de reversão de 7 bits

O código reverso de um tipo de documento SHALL ser o seu código de domínio com a ordem dos 7 bits invertida.

#### Scenario: Vetores da regra de reversão

- **WHEN** os códigos `0`, `1`, `5`, `16`, `32` e `63` são convertidos em código reverso
- **THEN** os valores obtidos são, respectivamente, `0`, `64`, `80`, `4`, `2` e `126`

#### Scenario: Bit sinalizador de tabela base

- **WHEN** qualquer código de `0` a `63` é convertido em código reverso
- **THEN** o bit mais à direita do resultado é `0`, deixando-o livre como sinalizador de tabela estendida

#### Scenario: Reversão é bijetora

- **WHEN** os 64 códigos da tabela base são convertidos em código reverso
- **THEN** os 64 valores obtidos são distintos entre si

#### Scenario: Ida e volta entre código e código reverso

- **WHEN** um tipo é resolvido por código e depois resolvido novamente pelo seu próprio código reverso
- **THEN** o tipo obtido é equivalente ao original, para todos os 64 códigos

### Requirement: Aderência à fonte da verdade

A tabela de tipos de documento usada pelo sistema SHALL corresponder exatamente ao conteúdo de `references/domain/tab-tpdoc.csv`, que é a fonte da verdade do domínio.

#### Scenario: Tabela divergente da fonte da verdade

- **WHEN** a tabela embutida no sistema diverge do CSV de referência em qualquer código, código reverso ou nome
- **THEN** a divergência é detectada e reportada como falha

#### Scenario: Cobertura da tabela

- **WHEN** a tabela do sistema é inspecionada
- **THEN** ela contém exatamente 64 entradas, com códigos de `0` a `63`, sem lacunas e sem repetições

### Requirement: Ausência de I/O e de dependências externas

A resolução de tipos de documento SHALL ocorrer sem leitura de arquivos em tempo de execução, e o pacote da biblioteca SHALL depender apenas da biblioteca padrão do Python.

#### Scenario: Resolução sem acesso a disco

- **WHEN** um tipo de documento é resolvido por código, por código reverso ou por nome
- **THEN** nenhum arquivo é aberto durante a operação

#### Scenario: Importação sem dependências externas

- **WHEN** o pacote é importado em um ambiente que contém apenas a biblioteca padrão do Python
- **THEN** a importação é bem-sucedida

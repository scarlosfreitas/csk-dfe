## ADDED Requirements

### Requirement: Tipo de documento Lote DFe

O código `31`, cujo código reverso é `124`, SHALL nomear o tipo de documento `Lote DFe` e SHALL deixar de ser tratado como reservado. O tipo SHALL ser resolvível pelas três formas de resolução: por código, por código reverso e por nome.

Rastreia o critério 30 do §8 do PRD.

#### Scenario: Resolução do Lote DFe por código

- **WHEN** um tipo de documento é resolvido pelo código `31`
- **THEN** o tipo resolvido tem código `31`, código reverso `124` e nome `Lote DFe`

#### Scenario: Resolução do Lote DFe por código reverso

- **WHEN** um tipo de documento é resolvido pelo código reverso `124`
- **THEN** o tipo resolvido tem código `31` e nome `Lote DFe`

#### Scenario: Resolução do Lote DFe por nome

- **WHEN** um tipo de documento é resolvido pelo nome `Lote DFe`
- **THEN** o tipo resolvido tem código `31` e código reverso `124`

## MODIFIED Requirements

### Requirement: Aderência à fonte da verdade

A tabela de tipos de documento usada pelo sistema SHALL corresponder exatamente ao conteúdo de `references/domain/tab-tpdoc.csv`, que é a fonte da verdade do domínio. O CSV de referência SHALL registrar `Lote DFe` como nome do código `31`.

#### Scenario: Tabela divergente da fonte da verdade

- **WHEN** a tabela embutida no sistema diverge do CSV de referência em qualquer código, código reverso ou nome
- **THEN** a divergência é detectada e reportada como falha

#### Scenario: Cobertura da tabela

- **WHEN** a tabela do sistema é inspecionada
- **THEN** ela contém exatamente 64 entradas, com códigos de `0` a `63`, sem lacunas e sem repetições

#### Scenario: O código 31 deixa de ser reservado

- **WHEN** o CSV de referência e a tabela do sistema são inspecionados na linha do código `31`
- **THEN** a coluna de nome não está vazia e contém `Lote DFe`

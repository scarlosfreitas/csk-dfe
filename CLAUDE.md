# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Todos os artefatos, specs, comentários, documentação e mensagens de commit são escritos em **português do Brasil**. Mensagens de commit no imperativo.

## O que é este repositório

Biblioteca Python que gera e decodifica o **CSK-DFE** (Composite Sharding Key), um identificador de partição de 64 bits para documentos fiscais eletrônicos brasileiros.

O pacote `csk_dfe` está implementado em `src/csk_dfe/`, com `pyproject.toml`, suíte `pytest` em `tests/` e notebooks de demonstração em `notebooks/`. As changes `class-tpdoc` e `class-all` já foram aplicadas: a resolução de tipos de documento (`TpDoc`) e as cinco funções do §4 do PRD (`generate`, `decode`, `hash_cnpj`, `to_base62`, `from_base62`) estão disponíveis.

## Cadeia de autoridade

Esta é a estrutura mais importante do projeto. Cada nível deriva do anterior e **nenhum pode contradizer o anterior**:

```
references/domain/     fonte da verdade do domínio
  ↓
specs/PRD.md           requisitos do produto, §8 com 27 critérios numerados (DEVE)
  ↓
openspec/changes/<n>/  proposal.md → specs/ → design.md → tasks.md
  ↓
código
```

- **`references/domain/csk_dfe_components.md`** — definição normativa dos componentes da chave e do algoritmo de hash, com parâmetros exatos.
- **`references/domain/tab-tpdoc.csv`** — tabela de tipos de documento, códigos 0–63, com a coluna `reverso`.
- **`specs/PRD.md`** — o §8 numera 27 critérios em linguagem normativa. Todo cenário WHEN/THEN de uma spec OpenSpec deve rastrear para um deles.

Nada deve ser suposto além do que esses arquivos permitem deduzir. **Em caso de lacuna, pergunte em vez de assumir** — é uma regra explícita do dono do projeto, não uma formalidade.

## Layout da chave e as armadilhas do domínio

```
sinal (1, sempre 0) | AAMMDD (20, <<43) | tpdoc reverso (7, <<36)
                    | hash do CNPJ (6, <<30) | random_number (30)
```

Pontos que já foram implementados errado ou documentados errado neste projeto:

- A data é o **decimal literal AAMMDD**, sem epoch, século fixo em 2000–2099. É deliberado: permite consulta SQL por faixa direto sobre a chave (`220101*2**43` a `230731*2**43`).
- O campo de documento grava o **código reverso** (reversão de 7 bits), nunca o código direto. O bit mais à direita do reverso é o sinalizador de tabela estendida, e por isso é sempre `0` para os códigos 0–63.
- O hash do CNPJ é **FNV-1a** (XOR antes da multiplicação), 32 bits, `& 63`, sobre a raiz de 8 caracteres, que pode ser alfanumérica. **Não é FNV-1** — a referência já esteve errada nesse ponto.
- O campo de 30 bits chama-se **`random_number`** em spec, código, testes e notebook — nome alinhado pela change `class-all`; o PRD e `references/domain/` já o chamavam de "aleatório". Usa gerador **não criptográfico**. Sequenciais foram rejeitados por causa de choques no processamento histórico (SQNFE do Catálogo 1.0).
- O CNPJ **não é recuperável** a partir da chave: o campo guarda um hash.
- A biblioteca **não garante unicidade** — é responsabilidade do consumidor.

Fora de escopo, não proponha sem que o escopo seja explicitamente reaberto: workers, tabela estendida de documentos, garantia determinística de unicidade e implementações em outras linguagens.

## Fluxo de trabalho OpenSpec

O projeto usa OpenSpec (schema `spec-driven`) para todo trabalho de implementação. Código não é escrito fora de uma change.

```bash
openspec list                              # changes ativas
openspec status --change "<nome>" --json   # artefatos e ordem de dependência
openspec show "<nome>"
openspec validate "<nome>" --strict        # rode sempre após editar artefatos
```

Slash commands: `/opsx:propose` (criar change + artefatos), `/opsx:update` (revisar artefatos existentes), `/opsx:apply` (implementar), `/opsx:archive`.

`openspec/config.yaml` tem um bloco `context:` preenchido que é injetado na geração de todo artefato. Ao mudar decisões de domínio, atualize-o junto.

## Convenções

- **`notebooks/` NÃO é referência.** Destina-se a notebooks de teste, demonstração e prototipação. O `.xlsx` e o `.ipynb` que estão lá são rascunhos históricos e foram explicitamente desqualificados como fonte da verdade.
- Ambiente virtual **fora da pasta do projeto** (via `UV_PROJECT_ENVIRONMENT`): o devcontainer é descartável e a árvore do projeto é bind mount.
- A biblioteca não deve depender de nada fora da stdlib. Ferramental de desenvolvimento (pytest) pode.

## Armadilhas do repositório

- **`.claude/agents/sdd-reviewer.md` está configurado para outro projeto** — o corpo do agente diz atuar "no projeto Copa2026 (ASP.NET Core + Blazor Server, .NET 10)". Os critérios de revisão SDD são aproveitáveis, o contexto de stack não.
- **`prompts/` são resíduos de um esqueleto de projeto**, exceto `1-create-prd.md`, que foi adaptado a este projeto. `3-create-agents.md` e `5-new-feature-script.md` descrevem subagentes de revisão Blazor/ASP.NET.
- **`scripts/*.sh` são infraestrutura do template de devcontainer** (`devcontainer-ai-cli`), não do CSK-DFE. Tratam de build de imagem, limpeza de containers e catálogo de plugins.

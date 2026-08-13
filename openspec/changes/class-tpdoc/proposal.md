## Why

O PRD está completo e a fonte da verdade é consistente, mas o repositório ainda não tem uma linha de código Python. O campo de 7 bits do CSK-DFE é o único que depende de uma tabela de domínio externa, e é também o mais sujeito a erro: a chave grava o código **reverso**, nunca o código direto. Implementar essa resolução primeiro fixa a parte mais delicada do layout antes que `generate()` e `decode()` dependam dela.

## What Changes

- Cria o pacote `csk_dfe` e o ferramental mínimo para executá-lo e testá-lo (`pyproject.toml` com uv, ambiente virtual fora da pasta do projeto, pytest como dependência de desenvolvimento).
- Introduz a classe `TpDoc`, com os construtores `from_name`, `from_cod` e `from_reverse_cod` e os métodos de instância `get_name`, `get_cod` e `get_reverse_cod`, conforme o §4 do PRD.
- Materializa a tabela de tipos de documento como um módulo Python gerado a partir de `references/domain/tab-tpdoc.csv`, eliminando I/O em tempo de execução.
- Acrescenta um gerador que produz esse módulo a partir do CSV, e um teste que falha se os dois divergirem — a fonte da verdade continua sendo o CSV.
- Acrescenta em `notebooks/` um notebook que demonstra `TpDoc` e seus métodos com saídas legíveis, servindo de documentação executável para quem for consumir a biblioteca.

Nenhuma mudança quebra comportamento existente: não há comportamento existente.

## Capabilities

### New Capabilities

- `tipo-documento`: resolução de tipos de documento fiscal por nome, por código e pelo código reverso gravado na chave, incluindo a regra de reversão de 7 bits e a semântica de códigos reservados.

### Modified Capabilities

Nenhuma. Não existem specs anteriores.

## Impact

**Código novo:**

- `pyproject.toml` — projeto uv, pacote `csk_dfe`, pytest em dependências de desenvolvimento.
- `src/csk_dfe/__init__.py` — superfície pública do pacote.
- `src/csk_dfe/tpdoc.py` — a classe `TpDoc`.
- `src/csk_dfe/_tabela_tpdoc.py` — tabela gerada, não editada à mão.
- `scripts/gerar_tabela_tpdoc.py` — gerador do módulo acima.
- `tests/` — testes dos requisitos desta capacidade.
- `notebooks/tpdoc.ipynb` — demonstração de uso, sem papel de verificação.

**Fonte da verdade consumida (não alterada):** `references/domain/tab-tpdoc.csv`.

**Requisitos do PRD cobertos:** critérios 10 a 15 do §8, mais o 26 (sem I/O) e o 27 (sem dependências fora da stdlib na biblioteca).

**Ambiente:** o ambiente virtual fica fora da pasta do projeto, via `UV_PROJECT_ENVIRONMENT`, já que o devcontainer é descartável e a árvore do projeto é um bind mount.

**Fora do escopo desta change:** `generate()`, `decode()`, hash do CNPJ, Base62, tabela estendida de documentos e workers.

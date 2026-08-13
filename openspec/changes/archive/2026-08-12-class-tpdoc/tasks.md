## 1. Esqueleto do projeto

- [x] 1.1 Criar `pyproject.toml` declarando o pacote `csk_dfe` com layout `src/`, sem dependências de runtime e com `pytest` em dependências de desenvolvimento
- [x] 1.2 Configurar `UV_PROJECT_ENVIRONMENT` para um caminho fora da árvore do projeto e registrar a variável no devcontainer
- [x] 1.3 Criar `src/csk_dfe/__init__.py` exportando `TpDoc` e as exceções do pacote
- [x] 1.4 Acrescentar ao `.gitignore` o que a build gera (`*.egg-info/`, `.pytest_cache/`) e `.ipynb_checkpoints/`
- [x] 1.5 Confirmar que `uv sync` cria o ambiente fora da pasta do projeto e que `uv run pytest` executa

## 2. Geração da tabela

- [x] 2.1 Escrever `scripts/gerar_tabela_tpdoc.py`, que lê `references/domain/tab-tpdoc.csv` e emite `src/csk_dfe/_tabela_tpdoc.py`
- [x] 2.2 No gerador, calcular a reversão de 7 bits a partir do `codigo` e abortar se divergir da coluna `reverso` do CSV
- [x] 2.3 No gerador, abortar se a tabela não tiver exatamente 64 entradas com códigos de 0 a 63, sem lacunas nem repetições
- [x] 2.4 Emitir no módulo gerado as entradas da tabela e os índices de busca por código, por código reverso e por nome
- [x] 2.5 Marcar o módulo gerado como não editável à mão, com aviso no cabeçalho
- [x] 2.6 Executar o gerador e versionar `src/csk_dfe/_tabela_tpdoc.py`

## 3. Exceções de domínio

- [x] 3.1 Definir a exceção base do pacote, derivada de `ValueError`
- [x] 3.2 Definir os erros distinguíveis exigidos pela spec: código fora da faixa, código reverso fora de 7 bits, código reverso de tabela estendida e nome inexistente

## 4. Classe TpDoc

- [x] 4.1 Implementar `TpDoc` como dataclass congelada com `codigo`, `reverso` e `nome`, com igualdade por valor
- [x] 4.2 Implementar `TpDoc.from_cod()`, rejeitando valores fora de 0 a 63
- [x] 4.3 Implementar `TpDoc.from_reverse_cod()`, rejeitando valores fora de 0 a 127 e rejeitando reversos ímpares com erro que identifique tabela estendida
- [x] 4.4 Implementar `TpDoc.from_name()`, rejeitando nome inexistente e nome vazio
- [x] 4.5 Implementar `get_cod()`, `get_reverse_cod()` e `get_name()`

## 5. Testes

- [x] 5.1 Testar resolução por código: código 0 resolve para NFe com reverso 0; código 2 resolve como reservado com reverso 32 e nome vazio; códigos fora de 0 a 63 são rejeitados
- [x] 5.2 Testar resolução por código reverso: 80 resolve para o código 5, NFCe; reverso ímpar é rejeitado como tabela estendida; valores fora de 0 a 127 são rejeitados
- [x] 5.3 Testar resolução por nome: `MDFe` resolve para o código 15 com reverso 120; nome inexistente e nome vazio são rejeitados
- [x] 5.4 Testar os vetores da reversão de 7 bits: 0→0, 1→64, 5→80, 16→4, 32→2, 63→126
- [x] 5.5 Testar que os 64 reversos são pares (bit sinalizador de tabela base) e distintos entre si
- [x] 5.6 Testar a ida e volta código → código reverso → código para os 64 códigos
- [x] 5.7 Testar a sincronia entre `_tabela_tpdoc.py` e `references/domain/tab-tpdoc.csv`, entrada a entrada
- [x] 5.8 Testar que a tabela tem exatamente 64 entradas, com códigos de 0 a 63, sem lacunas nem repetições
- [x] 5.9 Testar que nenhum arquivo é aberto durante a resolução de um tipo de documento
- [x] 5.10 Testar que o pacote importa sem dependências fora da stdlib

## 6. Notebook de demonstração

- [x] 6.1 Criar `notebooks/tpdoc.ipynb` importando `csk_dfe` do ambiente do projeto
- [x] 6.2 Demonstrar a resolução por código, por código reverso e por nome, exibindo o `TpDoc` resultante
- [x] 6.3 Exibir a tabela dos 64 códigos com código, código reverso e nome, marcando os reservados
- [x] 6.4 Mostrar a reversão de 7 bits com o binário do código e do reverso lado a lado, evidenciando o bit sinalizador de tabela estendida sempre em `0`
- [x] 6.5 Demonstrar os erros de domínio: código fora da faixa, código reverso ímpar e nome inexistente
- [x] 6.6 Manter o notebook sem asserções — a verificação é da suíte pytest

## 7. Fechamento

- [x] 7.1 Executar a suíte completa e confirmar que todos os cenários da spec `tipo-documento` estão cobertos
- [x] 7.2 Executar o notebook do início ao fim e versioná-lo com as saídas
- [x] 7.3 Confirmar que nenhuma afirmação do código, dos testes ou do notebook contradiz `references/domain/csk_dfe_components.md` ou o §8 do PRD

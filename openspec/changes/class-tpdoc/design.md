## Context

Ver `proposal.md` — Why. O repositório não tem código Python: esta change precisa decidir o esqueleto do pacote, não apenas a classe.

Duas restrições moldam o desenho:

- **Ambiente descartável.** O devcontainer monta a árvore do projeto como bind mount e é recriado com frequência. Um ambiente virtual dentro da pasta do projeto sobrevive à recriação do container com binários inválidos.
- **Fonte da verdade fora do pacote.** `references/domain/tab-tpdoc.csv` é documentação de domínio, não dado distribuível. Um pacote instalado não tem acesso a `references/`.

## Goals / Non-Goals

**Goals:**

- Estabelecer o layout do pacote que as próximas changes (`generate`, `decode`, Base62) vão herdar.
- Manter o CSV como fonte da verdade única, sem que a biblioteca dependa dele em tempo de execução.
- Tornar a divergência entre o CSV e o que o código usa uma falha de teste, não um bug silencioso.

**Non-Goals:**

- Publicação do pacote em índice (PyPI ou interno).
- Integração contínua.
- Qualquer decisão sobre a API de `generate()` e `decode()` além do que `TpDoc` precisa expor.

## Decisions

### Tabela como módulo Python gerado

A tabela vira `src/csk_dfe/_tabela_tpdoc.py`, um módulo com estrutura literal, produzido por `scripts/gerar_tabela_tpdoc.py` a partir do CSV.

*Por quê:* satisfaz o requisito de ausência de I/O de forma trivial e sobrevive à instalação do pacote, já que `references/` não é distribuída.

*Alternativas:* empacotar o CSV como dado e ler via `importlib.resources` mantém um arquivo só, mas paga I/O e configuração de dados de pacote; ler direto de `references/domain/` quebra assim que o pacote é instalado fora do repositório.

*Custo aceito:* o dado passa a existir em dois lugares. Mitigado pela decisão seguinte.

### Um teste guarda a sincronia com o CSV

Um teste lê `references/domain/tab-tpdoc.csv` e compara com `_tabela_tpdoc.py`, entrada a entrada. Ele roda no repositório, onde `references/` existe; não é um teste da biblioteca instalada.

*Por quê:* é o que converte a duplicação de dado em risco controlado. Sem ele, editar o CSV e esquecer de regenerar produz uma biblioteca silenciosamente errada — exatamente a classe de erro que a coluna `reverso` com `127` constante já produziu uma vez neste projeto.

### O gerador calcula o reverso e confere com o CSV

O gerador não copia a coluna `reverso` cegamente: calcula a reversão de 7 bits a partir do `codigo` e falha se o valor calculado divergir do que está no CSV.

*Por quê:* a coluna do CSV é mantida à mão e já esteve errada. Calcular e conferir detecta o erro na geração, em vez de propagá-lo para a chave.

*Alternativa:* confiar apenas na coluna. Rejeitada pelo histórico do arquivo.

### `TpDoc` imutável, com igualdade por valor

`TpDoc` é uma dataclass congelada com `codigo`, `reverso` e `nome`. Os construtores são métodos de classe que consultam índices pré-construídos no módulo da tabela; `get_cod()`, `get_reverse_cod()` e `get_name()` expõem os campos.

*Por quê:* o cenário de ida e volta da spec exige comparar dois `TpDoc` — igualdade por valor resolve isso sem código extra. Imutabilidade evita que uma instância compartilhada seja alterada por um consumidor.

*Sobre os métodos `get_*`:* são redundantes em Python, onde o acesso direto ao atributo bastaria. Mantidos porque o §4 do PRD os especifica nominalmente.

### Erros de domínio próprios

Entradas inválidas levantam exceções do pacote, derivadas de `ValueError`.

*Por quê:* a spec exige rejeição explícita em seis cenários distintos, e o consumidor precisa distinguir "código fora da faixa" de "nome inexistente" sem inspecionar mensagens. Derivar de `ValueError` mantém compatibilidade com quem já captura o tipo padrão.

### Layout `src/` e ambiente virtual fora do projeto

O pacote fica em `src/csk_dfe/`; o ambiente virtual é definido por `UV_PROJECT_ENVIRONMENT` apontando para fora da árvore do projeto.

*Por quê:* o layout `src/` impede que os testes importem o pacote pelo diretório de trabalho em vez da instalação, que é o que esconde erros de empacotamento. O ambiente fora da árvore atende ao §5 do PRD e à natureza descartável do devcontainer.

### Notebook é demonstração, não verificação

`notebooks/tpdoc.ipynb` mostra `TpDoc` em uso com saídas legíveis — a tabela dos 64 códigos, a reversão exibida em binário lado a lado com o decimal, e os erros de domínio sendo levantados. Ele não contém asserções e não decide se a implementação está correta; essa autoridade é da suíte pytest.

*Por quê:* um notebook com asserções seria uma segunda suíte, com os mesmos vetores, sem execução automática. Duas suítes sobre o mesmo contrato divergem — e a que ninguém roda é a que apodrece. Separar os papéis mantém uma única fonte de veredito.

*Por que existir, então:* o ponto do domínio mais sujeito a erro é o campo gravar o código reverso e não o direto. Isso é muito mais fácil de entender vendo `5 = 0000101` virar `80 = 1010000` do que lendo um assert. É documentação executável, e a pasta `notebooks/` é explicitamente destinada a isso no projeto.

*Alternativa:* não ter notebook. Rejeitada porque a regra de reversão é contraintuitiva o bastante para justificar uma explicação visual.

### pytest apenas como dependência de desenvolvimento

*Por quê:* o critério 27 do PRD proíbe dependências fora da stdlib **na biblioteca**, não no ferramental. Os vetores dos critérios 10 a 16 são naturalmente parametrizados, o que com `unittest` exigiria subteste manual repetitivo.

## Risks / Trade-offs

- **Tabela gerada diverge do CSV** → teste de sincronia dedicado; o gerador é idempotente e pode ser rerodado a qualquer momento.
- **Coluna `reverso` do CSV volta a ser editada com erro** → o gerador recalcula e confere, falhando na geração.
- **55 dos 64 códigos seguem sem nome** → `from_cod` e `from_reverse_cod` funcionam para todos; apenas `from_name` fica indisponível para os reservados, e a spec trata isso como comportamento esperado, não como defeito.
- **Métodos `get_*` destoam do idioma Python** → aceito por fidelidade ao PRD; nada impede expor os atributos também.
- **Escolhas de layout ficam difíceis de reverter depois** → esta é a primeira change justamente para que as seguintes herdem a decisão em vez de renegociá-la.
- **Notebook quebra sem ninguém perceber, por não ter execução automática** → aceito conscientemente: ele é documentação, e documentação desatualizada é um defeito de documentação, não de biblioteca. Executá-lo do início ao fim é tarefa de fechamento desta change.
- **Saída de execução do notebook polui os diffs** → o notebook é versionado com as saídas, por ser o que o torna legível no GitHub sem executar; em compensação, `.ipynb_checkpoints/` passa a ser ignorado pelo git.

## Migration Plan

Não se aplica: não há consumidores nem código anterior.

Analise profundamente esta implementação utilizando o Thinking Mode.

O objetivo desta revisão é avaliar a qualidade da aplicação antes de iniciar um novo ciclo de evolução utilizando o OpenSpec.

Antes de iniciar a análise:

- Compreenda a arquitetura da aplicação.
- Compreenda o domínio do problema.
- Compreenda as decisões arquiteturais adotadas neste projeto.
- Considere o CLAUDE.md com as regras globais do projeto
- Considere as SPECs existentes como fonte de verdade para as funcionalidades implementadas.
- Considere as regras de negócio já definidas para este projeto.

Durante a revisão utilize os seguintes subagentes especializados:

- review-architect
- review-performance
- review-blazor
- review-ui

Cada especialista deve analisar exclusivamente sua área de responsabilidade e produzir seu relatório técnico conforme definido em sua especificação.

Para a análise do Blazor considere que este projeto utiliza:

- Blazor Web App
- .NET 10
- Bootstrap
- JSInterop
- Prerendering habilitado

Durante a revisão identifique possíveis problemas relacionados ao ciclo de vida dos componentes, incluindo carregamento duplicado de dados causado pelo prerendering, uso inadequado do RenderMode, StateHasChanged, OnInitialized, OnInitializedAsync, OnParametersSet, OnParametersSetAsync, JSInterop e RenderFragment.

Após a conclusão das análises, utilize o subagente:

- review-manager

O review-manager deverá:

- Consolidar todos os relatórios produzidos.
- Eliminar recomendações duplicadas.
- Agrupar recomendações semelhantes.
- Identificar possíveis conflitos entre recomendações.
- Organizar todas as melhorias por categoria.
- Definir prioridades.
- Produzir um único plano consolidado de refinamento.

O review-manager não deverá reinterpretar nem modificar as conclusões técnicas produzidas pelos especialistas.

Sua responsabilidade é apenas consolidar, agrupar, eliminar duplicidades, identificar conflitos e definir prioridades.

O objetivo desta execução é exclusivamente produzir um plano técnico de refinamento.

Durante toda a revisão:

Não implemente alterações.

Não modifique arquivos.

Não escreva código.

Não proponha implementações detalhadas.

O relatório final deverá conter obrigatoriamente:

# Resumo Executivo

Apresente uma visão geral da qualidade atual da aplicação.

# Arquitetura

Liste todas as melhorias arquiteturais identificadas.

# Performance

Liste todas as melhorias relacionadas ao desempenho.

# Blazor

Liste todas as melhorias específicas do Blazor Web App.

# Interface do Usuário

Liste todas as melhorias relacionadas à UX, acessibilidade e responsividade.

# Plano Priorizado

Após consolidar os resultados, o review-manager deve:

- Exibir um resumo executivo no terminal.
- Salvar o relatório completo em:

docs/reviews/review-YYYY-MM-DD.md

Classifique todas as recomendações em:

- Alta Prioridade
- Média Prioridade
- Baixa Prioridade

Justifique a prioridade atribuída a cada recomendação.

# Próximos Passos

Com base no plano consolidado, apresente uma proposta de como essas melhorias podem ser organizadas em uma nova mudança utilizando o OpenSpec.

O resultado esperado desta revisão é um único relatório consolidado produzido pelo review-manager, servindo como base para a criação de uma nova SPEC e para o início de um novo ciclo de Spec-Driven Development.
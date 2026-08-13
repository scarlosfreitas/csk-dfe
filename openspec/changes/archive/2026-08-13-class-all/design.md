## Context

Ver `proposal.md` — Why. O esqueleto do pacote já foi decidido pela change `class-tpdoc`: layout `src/`, dataclass congelada, erros de domínio derivados de `ValueError`, tabela gerada sem I/O em tempo de execução, notebook como documentação e pytest como autoridade. Esta change herda tudo isso; o que ela precisa decidir é o que a change anterior deixou em aberto por só tratar um dos quatro campos.

Quatro restrições moldam o desenho:

- **A chave é aritmética pura.** Nenhum campo depende de estado, e o critério 26 do PRD exige tempo constante e ausência de I/O. Isso empurra a implementação para deslocamentos e máscaras sobre `int`, sem cache e sem estrutura auxiliar.
- **A assinatura pública está fixada pelo §4 do PRD.** As cinco funções e seus parâmetros estão nomeados lá. Desviar exige justificativa.
- **A chave é um contrato entre implementações.** O PRD prevê, nas evoluções futuras, uma implementação em outra linguagem com vetores de teste compartilhados. Qualquer detalhe deixado ao acaso aqui vira divergência entre implementações depois.
- **`references/domain/` é a fonte da verdade.** O algoritmo de hash tem parâmetros normativos; o código os reproduz literalmente, sem "otimizar".

## Goals / Non-Goals

**Goals:**

- Fechar o §4 do PRD com as cinco funções e o resultado nomeado de `decode()`.
- Manter a fronteira de erro explícita: toda entrada inválida vira uma exceção do pacote, distinguível por tipo.
- Deixar o campo de 30 bits testável sem estender a assinatura de `generate()`.
- Alinhar a nomenclatura do campo de 30 bits (`random_number`) entre spec, código, notebook e documentos de domínio.

**Non-Goals:**

- Funções auxiliares de faixa para SQL (limite inferior e superior de um período) — estão nas evoluções futuras do PRD.
- Validação de dígito verificador do CNPJ. O campo é um hash de particionamento, não uma validação cadastral; um CNPJ com DV errado ainda particiona de forma estável.
- Qualquer detecção de colisão. O critério de não-unicidade é explícito no §7 do PRD.
- Benchmark formal do custo de geração.

## Decisions

### Um módulo por capability

`src/csk_dfe/cnpj.py` (hash), `src/csk_dfe/chave.py` (`generate`/`decode`) e `src/csk_dfe/base62.py`. `__init__.py` reexporta as cinco funções e `CskDecodificado`, mantendo a API plana que o §4 do PRD descreve (`csk_dfe.generate()`, não `csk_dfe.chave.generate()`).

*Por quê:* o recorte espelha as três capabilities da spec, o que mantém rastreável qual módulo responde por qual requisito. `cnpj.py` em vez de `hash.py` para não sombrear o built-in em leitura de código.

*Alternativa:* um único `csk.py` com tudo. Rejeitada porque `chave.py` importaria de si mesmo conceitualmente — `generate()` depende de hash e de `TpDoc`, mas Base62 não depende de nenhum dos dois, e o módulo único esconderia essa independência.

### `decode()` devolve uma NamedTuple

`CskDecodificado(dhemi, tpdoc, hash_cnpj, random_number)`, um `typing.NamedTuple`.

*Por quê:* o notebook precisa de saída legível — `d.dhemi` diz o que uma tupla posicional não diz — e ao mesmo tempo o desempacotamento `dhemi, tpdoc, h, n = decode(k)` continua funcionando, que é a forma como o §4 do PRD lista o retorno. Custo zero: `NamedTuple` é stdlib e imutável.

*Alternativas:* dataclass congelada perde o desempacotamento posicional; `dict` perde o contrato explícito e o autocompletar. Ambas foram consideradas e descartadas com o dono do projeto.

### O campo de 30 bits chama-se `random_number`

Em todo lugar: nome do campo em `CskDecodificado`, variáveis, spec, testes e notebook.

*Por quê:* decisão do dono do projeto. O PRD e `references/domain/csk_dfe_components.md` hoje o chamam de "aleatório" / "número aleatório"; esta change os alinha, para que não sobrem dois nomes para o mesmo campo — que é exatamente o tipo de divergência que a implementação em outra linguagem herdaria.

*Custo aceito:* é a primeira vez que o código diverge do vocabulário em português do resto do projeto. Aceito por decisão explícita; o texto ao redor do identificador continua em português.

### `random.getrandbits(30)`, sem parâmetro de injeção

`generate(dhemi, tpdoc, cnpj)` fica exatamente com os três parâmetros do §4 do PRD. O módulo `random` é importado em `chave.py` e chamado diretamente.

*Por quê:* fidelidade à assinatura especificada. `getrandbits(30)` produz os 30 bits diretamente, uniformemente e sem módulo enviesado — é o Mersenne Twister, uniformemente distribuído e barato, e o PRD é explícito em não exigir gerador criptográfico.

*Testabilidade:* o teste dos extremos (`0` e `2**30 - 1`) faz `monkeypatch.setattr(csk_dfe.chave.random, "getrandbits", ...)`. Isso amarra o teste ao nome do módulo interno, o que é aceitável dentro do próprio repositório.

*Alternativas:* parâmetro `rng` ou `random_number` opcional. Ambas tornariam o teste mais direto, mas estendem a API pública além do PRD — e um `random_number` explícito abriria porta a chaves montadas à mão em produção.

### A data é validada por `datetime.date`, não por regra própria

Entrada `datetime` → `.date()`; entrada `date` → usada direta; entrada `str` → seis dígitos, fatiados em `AA`, `MM`, `DD` e passados a `date(2000 + AA, MM, DD)`. A janela de século é checada por comparação de ano.

*Por quê:* `date()` já rejeita `220230` e `991331` pelo calendário real, incluindo ano bissexto, sem que o pacote reimplemente essa lógica. `000000` cai no mesmo caminho (mês `0`). O erro de `date()` é capturado e reembalado num erro do pacote, para que o consumidor não precise distinguir `ValueError` de origens diferentes.

*Sobre `dhemi`:* o nome vem do XML de DF-e, onde `dhEmi` é data e hora. `generate()` aceita `datetime` e descarta a hora — a chave particiona por dia.

### `hash_cnpj()` normaliza antes de validar

Descarta todo caractere não alfanumérico, exige pelo menos 8 caracteres no que sobrou, e aplica o FNV-1a sobre os 8 primeiros.

*Por quê:* decisão do dono do projeto, nas duas metades. Aceitar CNPJ formatado é o caso real do consumidor, e fatiar os 8 primeiros de `"12.345.678/0001-95"` daria `"12.345.6"` — um segmento errado, produzido em silêncio, que só apareceria como partição desbalanceada muito depois. Rejeitar o que ficou curto demais evita o outro lado do mesmo problema: hashear uma entrada truncada e chamar isso de segmento.

*Sobre os bytes:* a raiz é codificada caractere a caractere pelo seu ponto de código, conforme o pseudocódigo normativo — um byte por caractere. Os vetores do critério 16 são todos ASCII; entrada fora de ASCII não é prevista pelo domínio e não é tratada de forma especial.

### `decode()` valida, não apenas fatia

Rejeita valor negativo, valor maior ou igual a `2**63`, campo de data que não forme uma data real, e campo de documento com o bit sinalizador de tabela estendida ligado — este último já vem de graça, por `TpDoc.from_reverse_cod()`.

*Por quê:* decisão do dono do projeto. Uma chave lida de um banco ou de um nome de arquivo pode ter sido corrompida ou vir de outra fonte; devolver `date` impossível ou tipo de documento inexistente empurraria o erro para longe da causa. O custo é de três comparações por chamada, irrelevante frente ao ganho de diagnóstico.

### Base62 de largura fixa, com alfabeto em ordem ASCII

Alfabeto `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`, 11 caracteres, `zfill('0')`.

*Por quê:* 62¹¹ ≈ 5,2 × 10¹⁹ cobre `2**63` ≈ 9,2 × 10¹⁸, enquanto 62¹⁰ ≈ 8,4 × 10¹⁷ não cobre — 11 é a largura mínima suficiente. A ordem do alfabeto é a ordem dos pontos de código (`'0' < '9' < 'A' < 'Z' < 'a' < 'z'`), e é isso, combinado com a largura fixa, que faz o critério 23 valer: com largura variável, `"z"` viria depois de `"10"` na comparação de strings, invertendo a ordem numérica.

*Por que não Base64 ou Crockford Base32:* Base64 tem `+` e `/`, que exigem escape em URL e não são ordenáveis; Base32 daria 13 caracteres.

### Erros de domínio novos

`CnpjInvalidoError`, `DataInvalidaError`, `ChaveInvalidaError` e `Base62InvalidoError`, todos sob uma base do pacote derivada de `ValueError`.

*Por quê:* mantém o padrão de `excecoes.py`. Hoje a base é `TpDocError`, específica de tipo de documento; ela passa a ser uma base do pacote (`CskDfeError`) com `TpDocError` derivando dela, para que o consumidor possa capturar tudo do pacote de uma vez sem perder a distinção por tipo. É uma generalização aditiva: quem captura `TpDocError` ou `ValueError` hoje continua funcionando.

### O notebook demonstra a chave inteira, sem asserções

`notebooks/csk-dfe.ipynb`, narrado: a chave montada campo a campo com o binário anotado, a faixa SQL de um período, o mesmo contribuinte caindo no mesmo segmento, o CNPJ que não volta, duas chamadas iguais dando chaves diferentes, o Base62 ordenando junto com o inteiro, e os erros sendo levantados.

*Por quê:* a mesma razão da change anterior, e ela vale ainda mais aqui — a decomposição de um inteiro de 64 bits em quatro campos é bem mais fácil de entender vendo `220101 | 1010000 | 001101 | ...` alinhado do que lendo um `assert`. Sem asserções, para que exista uma única fonte de veredito: o pytest.

*`notebooks/tpdoc.ipynb` permanece* como está, cobrindo só a reversão de bits. O novo notebook o referencia em vez de repeti-lo.

## Risks / Trade-offs

- **`monkeypatch` no `random` de `chave.py` amarra o teste ao módulo interno** → aceito; o teste vive no mesmo repositório e quebra alto se o módulo for renomeado. A alternativa custaria API pública.
- **A renomeação para `random_number` deixa PRD, `references/` e código temporariamente fora de sincronia** → o alinhamento dos documentos é tarefa desta change, não de uma futura; enquanto não estiver feito, a change não fecha.
- **Normalizar o CNPJ aceita entrada malformada em silêncio** (`"abc!!!12345678"` vira uma raiz válida) → mitigado apenas pelo piso de 8 caracteres. Aceito: validar cadastralmente o CNPJ é explicitamente um non-goal, e o campo é de particionamento.
- **`hash_cnpj()` não é reversível e o consumidor pode esperar que seja** → a spec e o §4 do PRD dizem o contrário, e o notebook demonstra o ponto explicitamente, mostrando que dois CNPJ diferentes podem cair no mesmo segmento.
- **Colisão de chave é possível e a biblioteca não avisa** → é o §7 do PRD. O notebook mostra a ordem de grandeza (2³⁰ por combinação de dia, tipo e segmento) para que o consumidor dimensione o próprio controle.
- **`generate()` com `datetime` descarta a hora** → é o comportamento correto para uma chave que particiona por dia, mas surpreende quem passa `dhEmi` esperando precisão de hora. Documentado na docstring e demonstrado no notebook.
- **A raiz alfanumérica torna o hash sensível à caixa** → trocar a caixa de um caractere muda o segmento na maioria dos casos (ex.: `"ABCDEFGH"` e `"ABCDEFGh"` caem em segmentos diferentes), mas não há garantia disso para todo par — com só 64 segmentos, duas raízes distintas podem coincidir por acaso após o `& 63`, como ocorre entre `"ABCDEFGH"` e `"abcdefgh"`, que colidem no segmento 13 apesar dos hashes de 32 bits completos serem diferentes. É consequência direta do algoritmo normativo, que opera sobre bytes; normalizar a caixa mudaria os vetores do critério 16. Mantido como está, e registrado na spec como cenário, com um par de exemplo que de fato diverge.
- **O notebook fica desatualizado sem execução automática** → mesmo trade-off já aceito na change anterior: executá-lo do início ao fim é tarefa de fechamento.

## Migration Plan

Não se aplica. A change é aditiva: nenhuma assinatura ou comportamento entregue por `class-tpdoc` muda. `TpDocError` passa a derivar de `CskDfeError`, o que amplia o que ele captura sem estreitar nada — código existente que captura `TpDocError` ou `ValueError` continua funcionando.

## Context

Ver `proposal.md — Why` para a motivação. O estado atual relevante:

- `generate(dhemi, tpdoc, cnpj)` em `src/csk_dfe/chave.py` monta a chave somando quatro deslocamentos fixos, e `hash_cnpj(cnpj)` é sempre chamado. O alias de tipo `DhEmi` e a função interna `_normalizar_dhemi` carregam o termo antigo.
- `CskDecodificado` é um `NamedTuple` de quatro campos, com `dhemi` na primeira posição — logo o rename é observável tanto por nome quanto por `_fields`.
- `src/csk_dfe/_tabela_tpdoc.py` é **gerado** por `scripts/gerar_tabela_tpdoc.py` a partir de `references/domain/tab-tpdoc.csv` e traz o aviso "NÃO EDITE ESTE ARQUIVO À MÃO". A entrada do código `31` é `_EntradaTpDoc(31, 124, "")`.
- A cadeia de autoridade do projeto exige que `references/domain/` e `specs/PRD.md` sejam alterados **antes** do código, porque nenhum nível pode contradizer o anterior. O §8 do PRD hoje numera 27 critérios; as specs desta change já rastreiam para os critérios 28, 29 e 30, que ainda não existem.

## Goals / Non-Goals

**Goals:**

- Uma única assinatura de `generate()` cobre os dois modos, com e sem CNPJ, sem função paralela e sem parâmetro-sinalizador redundante.
- O modo sem CNPJ preserva integralmente as propriedades de particionamento e de ordenação da chave: só os 36 bits menos significativos mudam de origem.
- O rename `dhemi` → `data` é total: nenhum resíduo do termo antigo em código, specs, PRD, testes ou notebooks.

**Non-Goals:**

- Marcar na chave que ela foi gerada sem CNPJ. Não há bit livre para isso, e criar um custaria faixa do `random_number` — decisão registrada abaixo.
- Alterar `hash_cnpj()`, `to_base62()`, `from_base62()` ou o layout de bits da chave.
- Rever os demais códigos reservados da tabela de tipos de documento. Só o `31` recebe nome.

## Decisions

### `cnpj` opcional na mesma função, com `None` como valor padrão

`generate(data, tpdoc, cnpj=None)`. Sem CNPJ, o campo de segmento recebe aleatório.

*Alternativa considerada:* uma função separada `generate_sem_cnpj()`. Rejeitada porque duplicaria a normalização de data, a validação e a documentação, e porque o consumidor típico decide entre os dois modos em tempo de execução, com um valor que pode ou não estar presente — passar `None` é mais natural do que ramificar a chamada.

*Alternativa considerada:* aceitar `cnpj=""` como equivalente a ausente. Rejeitada: string vazia hoje é entrada inválida para `hash_cnpj()` e deve continuar sendo rejeitada, para que um CNPJ vazio por bug do consumidor não vire silenciosamente uma chave sem CNPJ. Só `None` (ou a omissão do argumento) seleciona o modo sem CNPJ.

### Um único sorteio de 36 bits, não dois sorteios concatenados

No modo sem CNPJ, sortear `getrandbits(36)` e somar direto, em vez de sortear 6 bits e 30 bits separadamente. É uma chamada em vez de duas e torna óbvio, na leitura do código, que os 36 bits formam um bloco contínuo. No modo com CNPJ, `getrandbits(30)` permanece.

*Trade-off:* os dois modos passam a ter caminhos de código distintos para o sorteio. É um `if` de duas linhas e a alternativa — sempre sortear 36 bits e descartar 6 no modo com CNPJ — desperdiçaria entropia sem ganho de clareza.

### Nenhum marcador de origem na chave

Confirmado com o dono do projeto. Os 64 bits estão integralmente alocados; qualquer marcador sairia do `random_number`, reduzindo a faixa de desambiguação, ou do bit sinalizador de tabela estendida, que já tem dono. A consequência — `decode()` não distingue as duas origens — é documentada na docstring de `decode()` e no campo `hash_cnpj` da spec, não codificada na chave.

*Trade-off:* um consumidor que receba chaves de procedências mistas não pode filtrar por contribuinte com segurança. Mitigação: a documentação declara que `hash_cnpj` só é interpretável quando o consumidor sabe, por fora da chave, que ela foi gerada com CNPJ.

### Rename direto, sem alias nem `DeprecationWarning`

`data` substitui `dhemi` na assinatura, no `NamedTuple`, no alias de tipo (`DhEmi` → `Data`) e na função interna (`_normalizar_dhemi` → `_normalizar_data`). A biblioteca não tem versão publicada; um alias custaria complexidade permanente para proteger consumidores que não existem.

### `Lote DFe` entra pelo CSV e pelo gerador, nunca à mão

A alteração é `31,124,` → `31,124,Lote DFe` em `references/domain/tab-tpdoc.csv`, seguida da re-execução de `scripts/gerar_tabela_tpdoc.py`. Editar `_tabela_tpdoc.py` diretamente violaria o aviso do próprio arquivo e faria a próxima geração desfazer a mudança. O código `31` já estava reservado com reverso `124`, então nenhuma outra linha da tabela se move.

O nome `Lote DFe` segue a convenção de nomenclatura das demais linhas do CSV (`NFe`, `CTe Evento`, `MDFe Evento`) e é a string exata exigida por `TpDoc.from_name()`, que faz correspondência exata.

### O PRD é emendado antes do código

O §4 passa a descrever `data` e `cnpj` opcional; o §8 ganha os critérios 28, 29 e 30, nesta redação:

- **28.** `generate()` chamado sem `cnpj` **DEVE** preencher os 36 bits menos significativos da chave com valores do gerador aleatório, mantendo intactos os campos de data e de tipo de documento.
- **29.** Uma chave gerada sem `cnpj` **NÃO DEVE** ser distinguível, por inspeção da chave ou do resultado de `decode()`, de uma chave gerada com `cnpj`.
- **30.** `TpDoc.from_cod(31)` **DEVE** devolver código reverso `124` e nome `Lote DFe`, e `TpDoc.from_name("Lote DFe")` **DEVE** devolver o código `31`.

A numeração continua a série existente; nenhum critério de 1 a 27 é renumerado. Os critérios 3 e 6, que falam em "data de emissão", passam a falar em "data do documento".

### O notebook demonstra, o pytest reprova

O notebook novo em `notebooks/` é narrativa: células de markdown explicando cada campo da chave e células de código exibindo entradas e saídas legíveis (chave em decimal, em binário segmentado por campo, em Base62, e o resultado de `decode()`). Ele **não** contém `assert` nem qualquer verificação que possa falhar como teste — a autoridade sobre a corretude é a suíte `pytest`, e duplicar asserções criaria uma segunda fonte de verdade que envelhece sem ninguém perceber.

*Consequência para a manutenção:* o notebook pode ficar desatualizado sem quebrar a suíte. Aceito deliberadamente; a mitigação é ele exercitar apenas a API pública, que é estável por spec.

## Risks / Trade-offs

- **Consumidor interno já usa `generate(dhemi=...)` ou `.dhemi`** → A quebra é imediata e barulhenta (`TypeError` / `AttributeError`), nunca silenciosa. Foi aceita explicitamente pelo dono do projeto por não haver versão publicada.
- **`hash_cnpj` de uma chave sem CNPJ ser lido como segmento de contribuinte** → Documentado na docstring de `decode()`, no §4 do PRD e na spec `chave-composta`. Não há defesa técnica possível dentro do layout de 64 bits.
- **Chance de colisão sobe no modo com CNPJ e cai no modo sem CNPJ** → Sem CNPJ, o espaço de desambiguação por dia e tipo passa de 2³⁰ para 2³⁶; com CNPJ, é 2³⁰ por segmento. A biblioteca segue sem garantir unicidade nos dois modos, como já declarado na spec.
- **`_tabela_tpdoc.py` editado à mão em vez de regenerado** → A spec `tipo-documento` já exige aderência ao CSV e a suíte tem cenário de divergência; a checagem falha se o arquivo gerado sair de sincronia.
- **Resíduo de `dhemi` escapar em algum arquivo** → A verificação final é uma busca por `dhemi` em todo o repositório, incluindo `openspec/config.yaml` e os notebooks; a change só fecha com zero ocorrências fora do diretório `openspec/changes/archive/`, que é histórico imutável.

## Migration Plan

A ordem importa, porque cada nível da cadeia de autoridade valida o seguinte:

1. `references/domain/tab-tpdoc.csv` — o `Lote DFe`.
2. `specs/PRD.md` — §4 e §8.
3. `openspec/config.yaml` — o bloco `context:`.
4. Código, testes e notebook.

Não há dado persistido a migrar: chaves já emitidas continuam decodificando exatamente como antes, porque o layout de bits não muda. Rollback é a reversão do commit.

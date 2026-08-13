# csk-dfe

> **Composite Sharding Key** — identificador de partição de 64 bits para documentos fiscais eletrônicos brasileiros.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Dependências](https://img.shields.io/badge/depend%C3%AAncias-somente%20stdlib-brightgreen)](#especificações-técnicas)
[![Testes](https://img.shields.io/badge/testes-100%20passando-brightgreen)](#testes)

## Descrição

`csk-dfe` gera e decodifica o **CSK-DFE**, uma chave de 64 bits que carrega, em um único inteiro positivo, a informação necessária para particionar e ordenar grandes volumes de documentos fiscais eletrônicos (DF-e).

A chave é composta por quatro campos empacotados em bits:

| Bits | Deslocamento | Campo | Conteúdo |
| ---: | ---: | --- | --- |
| 1 | `<<63` | Sinal | Sempre `0`, garantindo representação positiva em `BIGINT` |
| 20 | `<<43` | Data | Data do documento em decimal literal `AAMMDD` |
| 7 | `<<36` | Documento | Código do tipo de documento, **em bits revertidos** |
| 6 | `<<30` | CNPJ base | Hash não criptográfico da raiz do CNPJ (ou aleatório, se omitido) |
| 30 | `<<0` | `random_number` | Número aleatório de desambiguação |

```
csk = AAMMDD * 2**43 + reverso * 2**36 + segmento * 2**30 + random_number
```

Três decisões de projeto explicam o formato:

- **A data é o decimal literal `AAMMDD`, sem *epoch*.** Isso permite consultar um período como faixa contínua diretamente sobre a chave, sem decodificar linha a linha: `WHERE csk >= 220101 * POWER(2, 43) AND csk < 230801 * POWER(2, 43)`. Como `AA` tem dois dígitos, a janela de século é fixa em **2000–2099**.
- **O campo de documento grava o código reverso**, não o código direto. A reversão de 7 bits deixa o bit mais à direita livre como sinalizador de tabela estendida (`0` = tabela base, `1` = tabela estendida).
- **O `random_number` é aleatório, nunca sequencial.** Sequenciais foram rejeitados deliberadamente: no processamento histórico, quando o contador gira os bits limites ocorre *reset*, e documentos que aparecem com meses de atraso colidem com sequências já emitidas — foi o que gerou choques no SQNFE do Catálogo 1.0.

## Objetivo

Otimizar o particionamento de uma plataforma de dados voltada a documentos e declarações fiscais, oferecendo uma chave que:

- permite **particionamento por data** (`AAMMDD`) e por **CNPJ base** (64 segmentos, agrupando filiais do mesmo contribuinte);
- permite **particionamento e filtragem por tipo de documento**;
- preserva a **ordenação cronológica na ordenação numérica** da própria chave;
- é gerada de forma **distribuída, sem coordenação entre processos**, sem I/O e em custo computacional constante;
- cabe em um `BIGINT` positivo, sendo utilizável direto em PostgreSQL, MinIO ou Iceberg.

**Público-alvo:** aplicações que manipulam documentos fiscais, como o Catálogo 2.0 e a `dfe-data-platform`, e armazenamentos massivos que demandam estratégias de particionamento.

### O que a biblioteca deliberadamente não faz

- **Não garante unicidade.** A desambiguação é probabilística (2³⁰ combinações por dia/tipo/segmento, ou 2³⁶ por dia/tipo sem CNPJ). Detectar e prevenir colisões é responsabilidade do consumidor.
- **Não permite recuperar o CNPJ a partir da chave.** O campo guarda um hash de 6 bits, não o valor — é impossível por construção.

## Instalação

Requer **Python 3.11+**. A biblioteca não tem nenhuma dependência fora da biblioteca padrão.

### Com uv

```bash
uv add git+https://github.com/scarlosfreitas/csk-dfe.git
```

### Com pip

```bash
pip install git+https://github.com/scarlosfreitas/csk-dfe.git
```

### Fixando uma versão

Recomendado em produção, para que uma alteração no `main` não altere o comportamento da geração de chaves. O projeto ainda não publica *tags* de versão, então fixe pelo commit:

```bash
uv add "git+https://github.com/scarlosfreitas/csk-dfe.git@b1194f32965fcd9124d934d87c0e7f75eab69489"
```

### Declarando como dependência

```toml
# pyproject.toml
[project]
dependencies = [
    "csk-dfe @ git+https://github.com/scarlosfreitas/csk-dfe.git@b1194f32965fcd9124d934d87c0e7f75eab69489",
]
```

### Desenvolvimento local

```bash
git clone https://github.com/scarlosfreitas/csk-dfe.git
cd csk-dfe
uv sync
uv run pytest
```

## Utilização

### Gerando uma chave

```python
from datetime import date
from csk_dfe import generate, TpDoc

tpdoc = TpDoc.from_name("NFCe")
csk = generate(date(2022, 1, 1), tpdoc, "11.111.111/0001-91")

print(csk)  # 1936034382484364903
```

O primeiro parâmetro é a **data do documento**: a data de emissão para documentos fiscais em geral, e a data de **recepção** para lotes de DF-e. Ele aceita três formas, todas produzindo o mesmo campo de data — a hora, quando presente, é descartada, porque a chave particiona por dia e não por instante:

```python
generate(datetime(2022, 1, 1, 23, 59, 59), tpdoc, cnpj)  # datetime
generate(date(2022, 1, 1), tpdoc, cnpj)                  # date
generate("220101", tpdoc, cnpj)                          # string AAMMDD
```

### Gerando sem CNPJ

O `cnpj` é opcional. Quando omitido, os 6 bits do segmento recebem aleatório do mesmo gerador que preenche o `random_number` — os 36 bits menos significativos passam a ser integralmente aleatórios:

```python
csk = generate("220101", TpDoc.from_name("Lote DFe"))
```

> [!IMPORTANT]
> Uma chave gerada sem CNPJ é **indistinguível** de uma gerada com CNPJ: não há marcador na chave nem no resultado de `decode()`. O campo `hash_cnpj` de uma chave sem CNPJ é ruído, e só deve ser interpretado como segmento de contribuinte quando o consumidor sabe, por fora da chave, que ela foi gerada com CNPJ.

Note ainda que `cnpj=""` **não** seleciona o modo sem CNPJ: string vazia é entrada inválida e continua sendo rejeitada, para que um CNPJ vazio por bug do consumidor não vire silenciosamente uma chave sem CNPJ. Só `None` (ou a omissão do argumento) seleciona esse modo.

### Decodificando uma chave

```python
from csk_dfe import decode

d = decode(1936034382484364903)

d.data           # datetime.date(2022, 1, 1)
d.tpdoc          # TpDoc(codigo=5, reverso=80, nome='NFCe')
d.hash_cnpj      # 13
d.random_number  # 686579303
```

`CskDecodificado` é um `NamedTuple`, então também é desempacotável posicionalmente:

```python
data, tpdoc, hash_cnpj, random_number = decode(csk)
```

### Resolvendo tipos de documento

`TpDoc` resolve um tipo nas três formas em que ele circula: por nome, por código de domínio (0–63) e pelo código reverso (o valor efetivamente gravado na chave).

```python
from csk_dfe import TpDoc

TpDoc.from_name("NFCe")        # TpDoc(codigo=5, reverso=80, nome='NFCe')
TpDoc.from_cod(5)              # TpDoc(codigo=5, reverso=80, nome='NFCe')
TpDoc.from_reverse_cod(80)     # TpDoc(codigo=5, reverso=80, nome='NFCe')

tpdoc.get_cod()          # 5
tpdoc.get_reverse_cod()  # 80  — é isto que vai gravado na chave
tpdoc.get_name()         # 'NFCe'
```

A tabela tem 64 códigos (0–63), dos quais 11 são nomeados e 53 permanecem reservados. Códigos reservados são válidos para `from_cod()` e `from_reverse_cod()`, mas não são resolvíveis por `from_name()`.

| Código | Reverso | Nome |
| ---: | ---: | --- |
| 0 | 0 | NFe |
| 1 | 64 | NFe Evento |
| 5 | 80 | NFCe |
| 6 | 48 | NFCe Evento |
| 10 | 40 | CTe |
| 11 | 104 | CTe Evento |
| 15 | 120 | MDFe |
| 16 | 4 | MDFe Evento |
| 31 | 124 | Lote DFe |
| 32 | 2 | EFD |
| 36 | 18 | PGDASD |

A fonte da verdade dessa tabela é `references/domain/tab-tpdoc.csv`; o módulo Python é **gerado** a partir dele por `scripts/gerar_tabela_tpdoc.py`.

### Segmentando o contribuinte

```python
from csk_dfe import hash_cnpj

hash_cnpj("11111111")            # 13
hash_cnpj("11.111.111/0001-91")  # 13  — mesma raiz, mesmo segmento
```

O hash considera apenas a **raiz de 8 caracteres** (que pode ser alfanumérica, no novo formato de CNPJ), descartando todo caractere não alfanumérico. É por isso que filiais de um mesmo contribuinte caem no mesmo segmento. O algoritmo é **FNV-1a** de 32 bits reduzido por `& 63`.

### Representação em texto (Base62)

```python
from csk_dfe import to_base62, from_base62

to_base62(1936034382484364903)  # '2J13aznB7B9'
to_base62(101 * 2**43)          # '0044GsGD4L2'  — largura fixa, padding à esquerda
from_base62("2J13aznB7B9")      # 1936034382484364903
```

São sempre **11 caracteres** do alfabeto `0-9A-Za-z`. A largura fixa é o que faz a ordenação lexicográfica dos textos acompanhar a ordenação numérica das chaves.

### Consultando por faixa de datas em SQL

O caso de uso que motiva o formato da chave:

```sql
-- documentos entre 01/01/2022 e 31/07/2023
SELECT * FROM documentos
WHERE csk >= 220101 * POWER(2, 43)
  AND csk <  230801 * POWER(2, 43);
```

```python
limite_inferior = 220101 * 2**43  # 1936028870281003008
limite_superior = 230801 * 2**43  # 2030147065618628608
```

### Tratamento de erros

Todas as exceções derivam de `CskDfeError`, que por sua vez deriva de `ValueError`:

```
CskDfeError
├── TpDocError
│   ├── CodigoForaDaFaixaError    código fora da faixa 0–63
│   ├── ReversoForaDaFaixaError   código reverso fora da faixa 0–127
│   ├── TabelaEstendidaError      código reverso ímpar (tabela estendida, fora de escopo)
│   └── NomeInexistenteError      nome não presente na tabela
├── CnpjInvalidoError             menos de 8 caracteres alfanuméricos
├── DataInvalidaError             fora do calendário ou fora da janela 2000–2099
├── ChaveInvalidaError            valor que não é uma chave CSK-DFE válida
└── Base62InvalidoError           texto Base62 inválido
```

```python
from csk_dfe import DataInvalidaError, generate, TpDoc

try:
    generate("220230", TpDoc.from_cod(5), "11111111000191")  # 30 de fevereiro
except DataInvalidaError as erro:
    print(erro)  # data '220230' não é um dia real do calendário
```

Datas são validadas contra o calendário real, e não apenas contra a representabilidade em 20 bits: `991331`, `220230` e `000000` são todas rejeitadas.

## Funcionalidade implementada

### API pública

| Função / classe | Descrição |
| --- | --- |
| `generate(data, tpdoc, cnpj=None)` | Compõe a chave de 64 bits. `cnpj` é opcional |
| `decode(csk)` | Decompõe a chave em `CskDecodificado(data, tpdoc, hash_cnpj, random_number)` |
| `hash_cnpj(cnpj)` | Segmenta o contribuinte em 0–63 pela raiz do CNPJ (FNV-1a) |
| `to_base62(csk)` | Codifica a chave em 11 caracteres, largura fixa |
| `from_base62(texto)` | Decodifica o texto Base62 de volta à chave |
| `TpDoc` | Resolução de tipos de documento por nome, código e código reverso |
| `CskDecodificado` | `NamedTuple` com os quatro campos decompostos |

### Comportamento coberto

- ✅ Composição e decomposição da chave, com *round-trip* garantido para toda entrada válida
- ✅ Data aceita como `datetime` (hora descartada), `date` ou string `AAMMDD`
- ✅ Particionamento e ordenação cronológica por faixa contínua de valores
- ✅ Validação de datas contra o calendário real e contra a janela de século 2000–2099
- ✅ Reversão de 7 bits do código de documento, com o bit sinalizador de tabela estendida sempre livre
- ✅ Tabela de 64 tipos de documento aderente ao CSV de referência, verificada por teste
- ✅ Hash FNV-1a de 32 bits sobre a raiz de 8 caracteres, aceitando raízes alfanuméricas
- ✅ Geração **sem CNPJ**, com os 36 bits menos significativos integralmente aleatórios
- ✅ Base62 de largura fixa preservando a ordenação lexicográfica
- ✅ Exceções de domínio tipadas para toda entrada inválida
- ✅ Geração sem I/O, em custo constante e sem estado compartilhado entre processos

### Testes

A suíte cobre **100 casos**, um para cada cenário especificado:

```bash
uv run pytest
```

### Especificações técnicas

- Python **3.11+**, sem nenhuma dependência fora da biblioteca padrão em tempo de execução
- **uv** como gerenciador de ambiente e dependências
- Tabela de tipos carregada como módulo Python literal — **nenhum I/O** em tempo de geração
- Ferramental de desenvolvimento: `pytest`, `ipykernel`, `nbclient`

## Próximas evoluções

Itens fora do escopo da versão atual, previstos para evoluções futuras:

- **Tabela estendida de tipos de documento**, usando o bit sinalizador já reservado no campo de documento
- **Identificação de *worker* na chave** (`worker_id` / `worker_num`), aproveitando bits do `random_number`
- **Garantia determinística de unicidade**, hoje responsabilidade do consumidor
- **Funções auxiliares de faixa** para consulta SQL, devolvendo os limites inferior e superior de um período
- **Implementação em outras linguagens**, como TypeScript, com vetores de teste compartilhados

## Estrutura do repositório

```
src/csk_dfe/            o pacote: chave, tpdoc, cnpj, base62, exceções
tests/                  suíte pytest, um caso por cenário especificado
references/domain/      fonte da verdade do domínio (componentes e tabela de tipos)
specs/PRD.md            requisitos do produto, com 30 critérios de aceitação numerados
openspec/               specs por capacidade e histórico de changes
scripts/                gerador da tabela de tipos a partir do CSV
notebooks/              notebooks de demonstração e prototipação
```

### Cadeia de autoridade

O projeto é conduzido por especificação. Cada nível deriva do anterior e nenhum pode contradizê-lo:

```
references/domain/  →  specs/PRD.md  →  openspec/  →  código
```

`references/domain/` é a fonte normativa do domínio; o `PRD.md` numera os critérios de aceitação; cada cenário das specs OpenSpec rastreia para um desses critérios; e todo código é escrito no contexto de uma *change*. Contribuições devem preservar essa cadeia.

## Glossário

| Termo | Significado |
| --- | --- |
| **CSK** | *Composite Sharding Key* — o identificador de 64 bits definido aqui |
| **DF-e** | Documento Fiscal eletrônico |
| **Raiz do CNPJ** | Os 8 primeiros caracteres do CNPJ, que identificam o contribuinte independentemente da filial |
| **Código reverso** | O código do tipo de documento com os 7 bits invertidos — a forma gravada na chave |
| **Tabela estendida** | Conjunto de tipos de documento fora da tabela base de 64 códigos |
| **SQNFE** | Identificador sequencial do Catálogo 1.0, cuja reciclagem gerou choques no processamento histórico |

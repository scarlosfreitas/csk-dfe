# PRD: CSK-DFE — Identificador de Partição Composta de 64 bits para documentos fiscais

## 1. Visão Geral

Biblioteca para geração e decodificação de um Identificador de Partição Composta (*Composite Sharding Key*) de 64 bits pensado para documentos fiscais.

Este identificador é pensado para otimizar o particionamento em uma plataforma de dados voltada a documentos e declarações fiscais, dividindo os 64 bits nas partes abaixo.

| Bits | Deslocamento | Campo | Conteúdo |
| --- | --- | --- | --- |
| 1 | `<<63` | Sinal | Sempre `0`, garantindo representação positiva em `BIGINT` |
| 20 | `<<43` | Data | Data de emissão em decimal no formato `AAMMDD` |
| 7 | `<<36` | Documento | Código do tipo de documento, **em bits revertidos** |
| 6 | `<<30` | CNPJ base | Hash não criptográfico da raiz do CNPJ |
| 30 | `<<0` | Aleatório | Número aleatório de desambiguação |

### 1.1 Data

A data é gravada como o **decimal literal `AAMMDD`** (ex.: 01/01/2022 → `220101`), sem *epoch*. Isso permite consultas SQL por faixa diretamente sobre a chave: documentos emitidos entre 01/01/2022 e 31/07/2023 estão em `220101*2**43` a `230731*2**43`.

Como `AA` tem apenas dois dígitos, a janela de século é **fixa em 2000–2099**.

### 1.2 Documento e reversão de bits

O valor gravado no campo de 7 bits **não** é o código do documento, e sim o seu **código reverso** — o código com os 7 bits invertidos na ordem.

A reversão existe para que o **bit mais à direita** do campo funcione como **sinalizador de tabela estendida**. Como a tabela base usa códigos de 0 a 63, o bit 6 do código original é sempre `0`; após a reversão de 7 bits ele se torna o bit 0 do valor gravado. Logo:

- bit mais à direita `= 0` → documento da tabela base;
- bit mais à direita `= 1` → documento de tabela estendida.

Exemplos da regra (código → reverso): `0 → 0`, `1 → 64`, `5 → 80`, `16 → 4`, `32 → 2`, `63 → 126`.

### 1.3 CNPJ base

Os documentos são particionados por dia, em arquivos de aproximadamente 128 MB. Para agrupar documentos de um mesmo contribuinte, são gerados 64 segmentos a partir de um hash não criptográfico uniformemente distribuído da **raiz de 8 caracteres** do CNPJ, que pode ser **alfanumérica**.

O algoritmo e seus parâmetros normativos estão definidos em `references/domain/csk_dfe_components.md` (FNV-1a de 32 bits, reduzido por `& 63`).

### 1.4 `random_number`

Os 30 bits menos significativos recebem o `random_number`, um número aleatório de desambiguação, oferecendo 1.073.741.824 possibilidades **por combinação de data, tipo de documento e segmento de CNPJ**.

O gerador deve ser uniformemente distribuído e de baixo custo computacional; **não** precisa ser criptográfico.

Números sequenciais são deliberadamente rejeitados: no processamento histórico, quando o sequencial gira os bits limites ocorre o *reset* do contador. Como é comum o aparecimento de documentos com meses de atraso, o risco de a chave desses documentos colidir com uma sequência já emitida é real — foi o que gerou choques no SQNFE do Catálogo 1.0.

---

## 2. Objetivos

* Criar uma biblioteca Python;
* Utilização mínima de dependências;
* Cálculo rápido e com custo computacional baixo;
* Permitir particionamento por data (`AAMMDD`) e por CNPJ base (64 segmentos);
* Permitir particionamento e filtragem por tipo de documento;
* Permitir geração distribuída sem coordenação entre processos.

---

## 3. Público-alvo

* Aplicações que utilizam documentos fiscais, como o Catálogo 2.0 e a `dfe-data-platform`.
* Armazenamentos de quantidade massiva de documentos fiscais que demandam estratégias de particionamento: PostgreSQL, MinIO ou Iceberg.

### 3.1 Glossário

| Termo | Significado |
| --- | --- |
| **CSK** | *Composite Sharding Key* — o identificador de 64 bits definido neste documento |
| **DF-e** | Documento Fiscal eletrônico |
| **Catálogo 1.0** | Sistema anterior de catalogação de documentos fiscais |
| **Catálogo 2.0** | Sistema sucessor, consumidor desta biblioteca |
| **dfe-data-platform** | Plataforma de dados de documentos fiscais, consumidora desta biblioteca |
| **SQNFE** | Identificador sequencial usado no Catálogo 1.0, cuja reciclagem gerou choques no processamento histórico |
| **Raiz do CNPJ** | Os 8 primeiros caracteres do CNPJ, que identificam o contribuinte independentemente da filial |
| **Tabela estendida** | Conjunto de tipos de documento fora da tabela base de 64 códigos |

---

## 4. Classes, funções e parâmetros

### `csk_dfe.generate()`

**Parâmetros de entrada:**

* **data:** data do documento — de emissão para documentos fiscais em geral, de recepção para lotes de DF-e (`datetime`, `date` ou string no formato `AAMMDD`)
* **tpdoc:** tipo de documento (objeto `TpDoc`)
* **cnpj:** CNPJ ou raiz do CNPJ (string, opcional). Quando omitido, os 6 bits reservados ao hash do CNPJ recebem bits do mesmo gerador aleatório que preenche o `random_number`

**Retorno:**

* **csk:** identificador de Partição Composta (inteiro de 64 bits)

### `csk_dfe.decode()`

**Parâmetros de entrada:**

* **csk:** identificador de Partição Composta (inteiro de 64 bits)

**Retorno:**

* **data:** data do documento (`date`, século 2000–2099)
* **tpdoc:** tipo de documento (objeto `TpDoc`)
* **hash_cnpj:** segmento do CNPJ base (inteiro de 0 a 63)
* **random_number:** número aleatório de desambiguação (inteiro de 0 a 2³⁰−1)

> O CNPJ **não** é recuperável a partir da chave: o campo de 6 bits guarda um hash, não o valor. `decode()` devolve o segmento, não o CNPJ. Quando a chave foi gerada sem CNPJ, o campo `hash_cnpj` traz ruído aleatório e não deve ser interpretado como segmento de contribuinte — a chave não carrega marcador de qual foi o caso.

### `csk_dfe.to_base62()`

**Parâmetros de entrada:**

* **csk:** identificador de Partição Composta (inteiro de 64 bits)

**Retorno:**

* string de **exatamente 11 caracteres**, alfabeto `0-9A-Za-z`, com padding `'0'` à esquerda

### `csk_dfe.from_base62()`

**Parâmetros de entrada:**

* string Base62 de 11 caracteres

**Retorno:**

* **csk:** identificador de Partição Composta (inteiro de 64 bits)

### `csk_dfe.hash_cnpj()`

**Parâmetros de entrada:**

* **cnpj:** CNPJ ou raiz do CNPJ (string)

**Retorno:**

* segmento (inteiro de 0 a 63)

### Classe `TpDoc`

**Construtores (métodos de classe):**

| Método | Entrada | Retorno |
| --- | --- | --- |
| `TpDoc.from_name(nome)` | nome do documento (string) | instância de `TpDoc` |
| `TpDoc.from_cod(codigo)` | código do documento (inteiro 0–63) | instância de `TpDoc` |
| `TpDoc.from_reverse_cod(reverso)` | código reverso (inteiro 0–127) | instância de `TpDoc` |

**Métodos de instância:**

| Método | Retorno |
| --- | --- |
| `get_name()` | nome do documento (string) |
| `get_cod()` | código do documento (inteiro 0–63) |
| `get_reverse_cod()` | código reverso, tal como gravado na chave (inteiro 0–127) |

---

## 5. Especificações técnicas

* A biblioteca é escrita em Python e usa **uv** como gerenciador de ambiente e dependências.
* A pasta do ambiente virtual fica **fora** da pasta do projeto.
* A biblioteca não realiza I/O em tempo de geração: a tabela de tipos de documento é carregada uma única vez.

### 5.1 Fonte de dados

Os dados de domínio são carregados a partir da pasta `references/domain/`:

* `csk_dfe_components.md` — definição normativa dos componentes da chave e do algoritmo de hash;
* `tab-tpdoc.csv` — tabela de tipos de documento.

### 5.2 Contrato de `tab-tpdoc.csv`

| Coluna | Tipo | Regra |
| --- | --- | --- |
| `codigo` | inteiro | Faixa **0 a 63**, sem lacunas e sem repetição — exatamente 64 linhas |
| `reverso` | inteiro | Reversão de **7 bits** de `codigo`. Valor lido do arquivo, não calculado pela biblioteca |
| `Tipo` | string | Nome do documento. Pode estar **vazio**: o código é então considerado **reservado** |

Códigos reservados são válidos para `from_cod()` e `from_reverse_cod()`, mas não são resolvíveis por `from_name()`.

---

## 6. Escopo

* Biblioteca Python de geração e decodificação da chave de 64 bits.
* Codificação e decodificação Base62 de largura fixa.
* Tabela de tipos de documento com códigos 0–63 e seus códigos reversos.

---

## 7. Fora de escopo

* **Workers** — qualquer funcionalidade vinculada a *workers* (`worker_id`, `worker_num`, reserva de bits para identificação de processo) está fora desta versão.
* **Tabela estendida de documentos** — apenas o bit sinalizador é definido; o cadastro e a resolução de códigos estendidos não fazem parte desta versão.
* **Garantia determinística de unicidade** — a biblioteca não detecta nem previne colisões; a unicidade é responsabilidade do consumidor.
* **Recuperação do CNPJ a partir da chave** — impossível por construção.
* **Implementação em outras linguagens**, como TypeScript.

---

## 8. Critérios de aceitação

### Composição da chave

1. A chave gerada **DEVE** ter o bit 63 igual a `0`.
2. A chave **DEVE** ser igual a `AAMMDD * 2**43 + reverso * 2**36 + hash * 2**30 + aleatorio`.
3. `decode()` **DEVE** devolver a data do documento, o tipo de documento e o segmento de CNPJ originalmente fornecidos a `generate()`, para qualquer entrada válida (*round-trip*).

### Data

4. Dada a data 01/01/2022, a chave gerada **DEVE** ser maior ou igual a `220101 * 2**43` e menor que `220102 * 2**43`.
5. Toda chave de um documento emitido em 2022 **DEVE** ser numericamente menor que toda chave de um documento emitido em 2023 — a ordenação numérica da chave reflete a ordenação cronológica.
6. `decode()` **DEVE** interpretar `AA` na janela 2000–2099 no campo de data do documento: `220101` devolve 01/01/2022.
7. `generate()` **DEVE** rejeitar datas inválidas com erro explícito, mesmo quando representáveis em 20 bits — por exemplo `991331`, `220230` e `000000`.
8. `generate()` **DEVE** rejeitar datas fora da janela 2000–2099.

### Tipo de documento

9. O campo de 7 bits da chave **DEVE** conter o código **reverso**, nunca o código direto.
10. A reversão de 7 bits **DEVE** satisfazer: `0→0`, `1→64`, `5→80`, `16→4`, `32→2`, `63→126`.
11. Para todo código de 0 a 63, o bit 0 do código reverso **DEVE** ser `0` (sinalizador de tabela base).
12. `TpDoc.from_cod(c).get_reverse_cod()` **DEVE** ser igual ao valor da coluna `reverso` da linha `c` de `tab-tpdoc.csv`.
13. `from_reverse_cod(from_cod(c).get_reverse_cod())` **DEVE** devolver o mesmo `TpDoc` que `from_cod(c)`, para todo `c` de 0 a 63.
14. `TpDoc.from_cod()` **DEVE** rejeitar valores fora da faixa 0–63.
15. `TpDoc.from_name()` **DEVE** rejeitar nomes não presentes na tabela, inclusive os de códigos reservados (`Tipo` vazio).

### Hash do CNPJ

16. `hash_cnpj()` **DEVE** produzir os valores: `"11111111"→13`, `"22222222"→5`, `"99999999"→29`, `"ABCDEFGH"→13`, `"1111111A"→61`.
17. `hash_cnpj()` **DEVE** produzir resultado sempre na faixa 0–63.
18. `hash_cnpj()` **DEVE** considerar apenas os 8 primeiros caracteres, produzindo o mesmo resultado para um CNPJ completo e para a sua raiz.
19. `hash_cnpj()` **DEVE** aceitar raízes alfanuméricas.

### `random_number`

20. Duas chamadas consecutivas de `generate()` com os mesmos argumentos **DEVEM** produzir chaves diferentes (com probabilidade 1 − 2⁻³⁰ por chamada).
21. O campo `random_number` **DEVE** ocupar toda a faixa de 0 a 2³⁰−1.

### Base62

22. `to_base62()` **DEVE** devolver exatamente 11 caracteres para qualquer chave válida, incluindo as de menor magnitude — `to_base62(101 * 2**43)` tem 9 dígitos significativos e **DEVE** receber dois `'0'` à esquerda.
23. Para quaisquer duas chaves `a < b`, `to_base62(a)` **DEVE** ser lexicograficamente menor que `to_base62(b)`.
24. `from_base62(to_base62(k))` **DEVE** ser igual a `k`.
25. `from_base62()` **DEVE** rejeitar strings com comprimento diferente de 11 ou com caracteres fora do alfabeto.

### Não funcionais

26. `generate()` **DEVE** executar em tempo constante em relação ao volume de chaves já geradas e **NÃO DEVE** realizar I/O.
27. A biblioteca **NÃO DEVE** depender de pacotes fora da biblioteca padrão do Python.

### Modo sem CNPJ e `Lote DFe`

28. `generate()` chamado sem `cnpj` **DEVE** preencher os 36 bits menos significativos da chave com valores do gerador aleatório, mantendo intactos os campos de data e de tipo de documento.
29. Uma chave gerada sem `cnpj` **NÃO DEVE** ser distinguível, por inspeção da chave ou do resultado de `decode()`, de uma chave gerada com `cnpj`.
30. `TpDoc.from_cod(31)` **DEVE** devolver código reverso `124` e nome `Lote DFe`, e `TpDoc.from_name("Lote DFe")` **DEVE** devolver o código `31`.

---

## 9. Evoluções futuras

* Tabela estendida de tipos de documento, usando o bit sinalizador já reservado.
* Identificação de *worker* na chave.
* Garantia determinística de unicidade.
* Funções auxiliares de faixa para consulta SQL (limites inferior e superior de um período).
* Implementação em outras linguagens, com vetores de teste compartilhados.

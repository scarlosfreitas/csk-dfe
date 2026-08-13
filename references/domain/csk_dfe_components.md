# Componentes da chave Identificador de Partição Composta (Composite Sharding Key) de 64 bits pensado para documentos fiscais.

## Data

A representação da data em decimais será AAMMDD. Não será utiliza uma data inicial (epoch), assim, conseguimos fazer consultas sql de forma simples com data na chave.

Exemplo: documentos emitidos entre 01/01/2022 a 31/07/2023 seriam: `220101*2**43 a 230731*2**43`

## Documento

Existirá uma tabela com 64 documentos gerais e mais comuns (codigo 0 a 63). Os demais códigos poderão ser utilizados de forma flexível ou utilizando uma tabela estendida. Os numeros que comporão a chave sofreram Reversão de Bits, a fim de deixar o bit mais a direita como sinalização da tabela expandida. Caso seja necessário, esse bit poderá ser utilizado como parte da identificação do worker. 

## CNPJ base

Os documentos serão particionados por dia, em arquivos geralmente de 128mb. A fim de agrupar os documentos de mesmos contribuintes, serão gerados 64 segmentos a partir do hash não criptográfico uniformemente distribuído do CNPJ base.

O algoritmo utilizado será o FNV-1a pelas seguintes razões:
1. **Extremamente leve:** Usa apenas operações de XOR (`^`) e multiplicação.
2. **Trata strings perfeitamente:** Lida nativamente com o novo formato de CNPJ (que agora possui raízes alfanuméricas de 8 posições).
3. **Efeito Avalanche:** Mesmo que dois CNPJs mudem apenas um caractere, o hash muda completamente, evitando que arquivos fiquem acumulados na mesma divisão.

Parâmetros normativos, necessários para que a partição seja reproduzível entre implementações:

| Parâmetro | Valor |
| --- | --- |
| Largura | 32 bits, aritmética sem sinal (todo resultado truncado por `& 0xFFFFFFFF`) |
| Offset basis | `0x811C9DC5` |
| Primo | `0x01000193` |
| Ordem das operações | XOR do byte **antes** da multiplicação (é o que distingue FNV-1a de FNV-1) |
| Entrada | Bytes da raiz de 8 caracteres do CNPJ, um byte por caractere |
| Redução para 6 bits | `& 63` |

Pseudocódigo normativo:

```text
hash := 0x811C9DC5
para cada byte b da raiz:
    hash := hash XOR b
    hash := (hash * 0x01000193) & 0xFFFFFFFF
retorna hash & 63
```

## Número Aleatório

A fim evitar choques ao criar chaves, serão utilizados  30 bits para geração de  número aleatório, garantindo 1.073.741.824 possibilidade para um dia. Os últimos dígitos podem ser utilizados para indicação de workers.

O algoritmo de geração deve ser uniformemente distribuído, geração com baixo consumo computacional e não precisa ser criptográfico.

Porque deve-se evitar números sequenciais: se for feito o processamento histórico, quando o sequencial girar os bits limites, resulta no reset do sequencial. Como é comum o aparecimento de documentos com meses de atraso, a chave dele chocar em uma sequencia de chaves é real. O SQNFE do Catalogo 1.0 gerou alguns choque no processamento histórico.

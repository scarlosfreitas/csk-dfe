Este é um projeto que serve se esqueleto para outros projetos baseados em devcontainer e claude code.

São instaladas as ferramentas necessárias ao desenvolvimento e prototipação, como python uv, npm e sudo.

Leia integralmente todos os arquivos da pasta ./references

A pasta ./references contém a fonte da verdade dos dados.

Não faça nenhuma suposição que não possa ser deduzida desses arquivos. E me pergunte se ficar alguma lacuna.
 
Construa o PRD.md seguindo as melhores práticas de Spec Driven Development, manuais de utilização do OpenSpec e o modelo a seguir:


# Modelo de PRD.md
# PROD - Nome do Projeto

## 1. Visão Geral

texto

---

## 2. Objetivos

texto

* objetivo 1
* objetivo 2
* objetivo 3
* objetivo 4
* objetivo 5

---
## 2. Público alvo

* público 1
* público 2
* público 3
* público 4

---
## 4. Navegação principal

texto

---

## N. Fonte de dados

Os dados iniciais serão carregados através de Seed a partir da pasta ./fontes do projeto

Dados initiais previstos:

* item 1 (informação, não é o nome do arquivo)
* item 2
* item 3

---

## N+1. Estrutura do protótipo

### Estrutura do protótipo

A estrutura esperada é:

'''text (bloco de código com estrutura de pasta)
prototipo/
	css/
		site.css < estilo globais
	js/
		site.js
	docs/
		PRD.md
	fontes/
		documento.txt
		...
	pagina 1.html
	...
'''

---

## N+2. Fora do escopo

Não faz parte da primeira versão

* item 1
* item 2
* item 3

--- 

--- 

## N+3 Critérios de aceitação


## N+4 Evoluções Futuras

### Estrutura do protótipo

* item 1
* item 2
* item 3
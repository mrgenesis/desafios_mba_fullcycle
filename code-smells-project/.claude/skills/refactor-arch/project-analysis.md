# Heurísticas de Análise de Projeto

Use este documento na Fase 1 para detectar a stack, o banco de dados, o domínio e a arquitetura atual do projeto.

---

## Detecção de Linguagem

| Sinal no projeto                           | Linguagem   |
| ------------------------------------------ | ----------- |
| `requirements.txt` ou `pyproject.toml`     | Python      |
| `package.json` (sem `requirements.txt`)    | Node.js     |
| `pom.xml` ou `build.gradle`                | Java/Kotlin |
| `Gemfile`                                  | Ruby        |
| `go.mod`                                   | Go          |
| `composer.json`                            | PHP         |

Se houver ambiguidade (ex.: projeto polyglot), liste todas as linguagens encontradas e identifique a principal pelo entry point.

---

## Detecção de Framework

Para cada framework, verifique **dois lugares distintos** — basta encontrar o sinal em qualquer um deles:

1. **Arquivo de dependências** — `requirements.txt` / `pyproject.toml` (Python) ou `package.json` (Node.js).
2. **Arquivos de código-fonte** — arquivos `.py`, `.js`, `.ts` do projeto (nunca em arquivos de configuração).

### Python
| Onde buscar          | Sinal a procurar              | Framework |
| -------------------- | ----------------------------- | --------- |
| `requirements.txt`   | linha contendo `flask`        | Flask     |
| Arquivos `.py`       | `from flask import`           | Flask     |
| `requirements.txt`   | linha contendo `django`       | Django    |
| Arquivos `.py`       | `import django`               | Django    |
| `requirements.txt`   | linha contendo `fastapi`      | FastAPI   |
| Arquivos `.py`       | `from fastapi import`         | FastAPI   |

### Node.js
| Onde buscar          | Sinal a procurar                    | Framework |
| -------------------- | ----------------------------------- | --------- |
| `package.json`       | chave `"express"` em dependencies   | Express   |
| Arquivos `.js`/`.ts` | `require('express')` ou `import … from 'express'` | Express |
| `package.json`       | chave `"fastify"` em dependencies   | Fastify   |
| Arquivos `.js`/`.ts` | `require('fastify')` ou `import … from 'fastify'` | Fastify |
| `package.json`       | chave `"koa"` em dependencies       | Koa       |
| Arquivos `.js`/`.ts` | `require('koa')` ou `import … from 'koa'`         | Koa      |
| `package.json`       | chave `"@nestjs/core"` em dependencies | NestJS |

### Versão
Leia a versão no arquivo de dependências (`requirements.txt`, `package.json`). Exemplo: `Flask==2.3.0` ou `"express": "^4.18.0"`.

---

## Detecção de Banco de Dados

Para cada banco, verifique **dois lugares distintos** — basta encontrar o sinal em qualquer um deles:

1. **Arquivo de dependências** — `requirements.txt` / `pyproject.toml` (Python) ou `package.json` (Node.js).
2. **Arquivos de código-fonte** — arquivos `.py`, `.js`, `.ts` do projeto.

| Onde buscar           | Sinal a procurar                              | Banco de dados     |
| --------------------- | --------------------------------------------- | ------------------ |
| `requirements.txt`    | linha contendo `sqlite3`                      | SQLite             |
| Arquivos `.py`        | `import sqlite3`                              | SQLite             |
| Qualquer pasta        | arquivo com extensão `.db` ou `.sqlite`       | SQLite             |
| `requirements.txt`    | linha contendo `SQLAlchemy`                   | SQL via SQLAlchemy |
| Arquivos `.py`        | `from sqlalchemy import` ou `import sqlalchemy` | SQL via SQLAlchemy |
| `requirements.txt`    | linha contendo `psycopg2`, `pg` ou `postgres` | PostgreSQL         |
| Arquivos `.py`        | `import psycopg2`                             | PostgreSQL         |
| `requirements.txt`    | linha contendo `mysql-connector` ou `pymysql` | MySQL              |
| Arquivos `.py`        | `import pymysql` ou `import mysql.connector`  | MySQL              |
| `package.json`        | chave `"mongoose"` em dependencies            | MongoDB            |
| Arquivos `.js`/`.ts`  | `require('mongoose')` ou `import … from 'mongoose'` | MongoDB      |
| `package.json`        | chave `"mysql2"` em dependencies              | MySQL              |
| Arquivos `.js`/`.ts`  | `require('mysql2')` ou `import … from 'mysql2'`     | MySQL        |
| `package.json`        | chave `"sequelize"` em dependencies           | SQL via Sequelize  |
| Arquivos `.js`/`.ts`  | `require('sequelize')` ou `import … from 'sequelize'` | SQL via Sequelize |

Para identificar tabelas/entidades: leia arquivos `models.py`, `models/`, `schema.sql`, ou qualquer `CREATE TABLE` / `db.define(...)`.

---

## Detecção de Domínio

Infira o domínio a partir dos **nomes de rotas, tabelas e entidades** encontrados:

| Vocabulário encontrado                              | Domínio inferido       |
| --------------------------------------------------- | ---------------------- |
| `produto`, `pedido`, `carrinho`, `checkout`        | E-commerce             |
| `course`, `enrollment`, `lesson`, `student`        | LMS / EAD              |
| `task`, `todo`, `assignee`, `due_date`             | Gerenciador de tarefas |
| `patient`, `appointment`, `doctor`, `prescription` | Saúde                  |
| `employee`, `payroll`, `department`                | RH / ERP               |
| `post`, `comment`, `like`, `feed`                  | Rede social / Blog     |

Se o vocabulário não encaixar em nenhuma categoria, descreva o domínio com base no propósito inferido da aplicação.

---

## Classificação da Arquitetura Atual

Avalie a estrutura de pastas e a distribuição de responsabilidades:

| Classificação               | Critérios                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| **Monolítica**              | ≤ 3 arquivos principais; roteamento, lógica de negócio e acesso a dados no mesmo arquivo  |
| **Parcialmente organizada** | Há separação em pastas (ex.: `models/`, `routes/`), mas Controllers são inexistentes ou a lógica de negócio está nas Routes |
| **Próxima de MVC**          | Models, Controllers e Routes em pastas separadas; responsabilidades relativamente distintas, mas com violações pontuais |

Identifique qual classificação melhor descreve o projeto e justifique em uma linha.

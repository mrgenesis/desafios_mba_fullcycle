# Catálogo de Anti-Patterns

Use este documento na Fase 2 para auditar o código do projeto. Para cada anti-pattern listado, verifique se o **sinal de detecção** ocorre nos arquivos de código-fonte. Não invente findings sem sinal correspondente; não pule nenhum item sem checar.

Severidades: **CRITICAL** → **HIGH** → **MEDIUM** → **LOW**

---

## 1. God File / Monolítico

**Severidade:** CRITICAL

**Sinal de detecção:** Um único arquivo de entrada (ex.: `app.py`, `index.js`, `main.py`, `server.js`) concentra rotas, lógica de negócio e acesso a dados. Sinais concretos:
- O arquivo tem mais de 150 linhas **e** contém ao mesmo tempo definições de rotas (`@app.route`, `app.get`, `router.get`), queries ao banco (`db.execute`, `session.query`, `Model.find`) e cálculos de negócio.
- Não existem subpastas `models/`, `controllers/`, `routes/` ou `services/` com mais de um arquivo cada.

**Impacto:** Qualquer alteração impacta o sistema inteiro; testabilidade zero; onboarding lento.

**Recomendação:** Separar em camadas MVC conforme `architecture-guidelines.md`.

**Categoria:** Refatoração estrutural

---

## 2. Fat Route (Lógica de Negócio na Rota)

**Severidade:** CRITICAL

**Sinal de detecção:** Dentro de um handler de rota (`@app.route`, `app.get`, `router.post`, etc.), encontra-se **mais de uma** das seguintes responsabilidades ao mesmo tempo:
- Acesso direto ao banco (query, ORM call, raw SQL).
- Cálculo de regra de negócio (condicionais sobre dados de domínio, cálculos financeiros, validações de estado).
- Serialização/formatação da resposta além de um simples `return jsonify(obj)`.

Exemplo de sinal em Python:
```python
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    total = sum(item['preco'] * item['qtd'] for item in data['itens'])  # regra de negócio
    db.execute('INSERT INTO pedidos ...')                                  # acesso a dados
    return jsonify({'total': total, 'status': 'criado'}), 201
```

**Impacto:** Rota não testável isoladamente; duplicação de lógica em múltiplas rotas.

**Recomendação:** Mover lógica para um Controller; mover acesso a dados para o Model.

**Categoria:** Refatoração estrutural

---## 3. Acesso Direto ao Banco na Rota

**Severidade:** CRITICAL

**Sinal de detecção:** Chamadas de ORM ou SQL raw **dentro** de um handler de rota, sem passar por um Model ou repositório. Procure nos arquivos de rotas por:
- Python/SQLAlchemy: `db.session.query(`, `db.session.add(`, `db.execute(`
- Python/sqlite3: `cursor.execute(`, `conn.execute(`
- Node/Sequelize: `Model.findAll(`, `Model.create(` chamados diretamente dentro de `app.get(`, `router.post(`
- Node/mongoose: `Model.find(`, `Model.save(` dentro de handlers de rota

**Impacto:** Duplicação de queries; impossibilidade de trocar o banco sem editar rotas.

**Recomendação:** Encapsular queries no Model ou em um repositório; a rota só chama o Controller.

**Categoria:** Refatoração estrutural

---## 4. Segredo / Configuração Hardcoded

**Severidade:** CRITICAL

**Sinal de detecção:** Nos arquivos `.py`, `.js` ou `.ts`, procure por strings literais atribuídas diretamente a variáveis de configuração — **não** lidas de `os.environ`, `process.env` ou de um arquivo de config. Exemplos de sinais:
- `SECRET_KEY = "minha-chave-secreta"` ou `app.config['SECRET_KEY'] = 'abc123'`
- `DB_URL = "postgresql://user:senha@localhost/db"`
- `API_KEY = "sk-..."` ou `TOKEN = "Bearer xpto"`
- String de conexão com usuário e senha embutidos: `mysql://root:root@localhost`

**Impacto:** Segredo versionado no repositório; ambientes diferentes exigem edição de código.

**Recomendação:** Ler de variáveis de ambiente com fallback apenas para dev local; nunca commitar segredos reais.

**Categoria:** Correção obrigatória

---

## 5. SQL Injection

**Severidade:** CRITICAL

**Sinal de detecção:** Valores recebidos do request são concatenados diretamente em strings de SQL — sem uso de parâmetros nomeados, placeholders (`?`, `%s`, `:param`) ou ORM. Procure nos arquivos de código-fonte por:
- Python: `f"SELECT ... WHERE id = {data['id']}"` ou `"INSERT INTO ... VALUES ('" + valor + "')"` passados para `cursor.execute(` ou `db.execute(`.
- Node.js: template literals ou concatenação de string dentro de `db.query(`, `connection.execute(`, `pool.query(`.

Exemplo de sinal em Python:
```python
nome = request.json['nome']
cursor.execute(f"SELECT * FROM usuarios WHERE nome = '{nome}'")  # vulnerável
```

**Impacto:** Atacante pode ler, modificar ou deletar qualquer dado do banco; em alguns bancos permite execução de comandos no servidor.

**Recomendação:** Usar sempre parâmetros parametrizados: `cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (nome,))` ou a API de ORM equivalente.

**Categoria:** Correção obrigatória

---## 6. Tratamento de Erros Duplicado

**Severidade:** HIGH

**Sinal de detecção:** Blocos `try/except` (Python) ou `try/catch` (JS) com tratamento de HTTP error (retorno de `status 500`, log de erro genérico, `return jsonify({'error': ...})`) repetidos em **duas ou mais** rotas ou funções diferentes, com conteúdo idêntico ou muito semelhante.

**Impacto:** Comportamento inconsistente de erros entre endpoints; manutenção multiplicada.

**Recomendação:** Centralizar em um error handler global (Flask: `@app.errorhandler`; Express: middleware de 4 argumentos `(err, req, res, next)`).

**Categoria:** Correção obrigatória

---## 7. Ausência de Validação na Fronteira

**Severidade:** MEDIUM

**Sinal de detecção:** Dados de entrada (`request.json`, `request.form`, `req.body`) são usados diretamente em queries ou lógica de negócio **sem** nenhuma verificação de presença/tipo. Sinais:
- `data = request.json` seguido imediatamente de `data['campo']` sem checar se a chave existe.
- `req.body.campo` usado em query sem nenhum middleware de validação (`joi`, `zod`, `pydantic`, `marshmallow`).
- Ausência de qualquer `if 'campo' not in data` ou schema de validação.

**Impacto:** Erros 500 em vez de 400 para input inválido; superfície de injeção de dados.

**Recomendação:** Validar com schema (Pydantic, Marshmallow, Joi, Zod) antes de usar os dados.

**Categoria:** Correção obrigatória

---## 8. Estado Global Mutável

**Severidade:** HIGH

**Sinal de detecção:** Variáveis no escopo de módulo (fora de qualquer função ou classe) que são **escritas** durante o ciclo de vida da aplicação — não apenas lidas como constante. Sinais:
- `lista_de_pedidos = []` no topo do arquivo, com `lista_de_pedidos.append(...)` dentro de rotas.
- `contador = 0` com `contador += 1` em handlers.
- Dicionários como `cache = {}` populados em tempo de request.

**Impacto:** Estado compartilhado entre requests em ambientes multi-thread; bugs de concorrência.

**Recomendação:** Usar banco de dados ou cache externo (Redis); eliminar estado mutável em módulo.

**Categoria:** Refatoração estrutural

---## 9. Acoplamento Forte / Ausência de Injeção de Dependência

**Severidade:** HIGH

**Sinal de detecção:** Um módulo de alto nível (rota, controller) instancia ou importa diretamente uma implementação concreta de baixo nível (conexão ao banco, cliente HTTP, serviço externo) em vez de receber a dependência por parâmetro. Sinais nos arquivos de código-fonte:
- Python: `from database import db` ou `import sqlite3; conn = sqlite3.connect(...)` dentro de um controller ou rota, sem que a conexão seja passada como argumento.
- Node.js: `const db = require('../db')` ou `const axios = require('axios')` referenciados diretamente no corpo de um handler, sem injeção via parâmetro ou container.
- Criação de objetos com `new ConcreteService()` dentro de funções de rota ou controller.

**Impacto:** Impossível substituir a implementação (ex.: trocar banco real por mock em testes) sem alterar o código do caller; alto acoplamento entre camadas.

**Recomendação:** Passar dependências como parâmetro (injeção manual) ou centralizá-las no composition root (`app.py`, `app.js`); nunca instanciar dependências de infraestrutura dentro de controllers ou rotas.

**Categoria:** Refatoração estrutural

---## 10. Violação de SRP (Classe ou Função com Múltiplas Responsabilidades)

**Severidade:** MEDIUM

**Sinal de detecção:** Uma única função ou classe executa ao mesmo tempo **dois ou mais** destes grupos:
1. Acesso a dados (query, leitura de arquivo, chamada de API externa).
2. Regra de negócio (cálculo, validação de domínio, decisão de fluxo).
3. Formatação de resposta ou serialização.

Sinal prático: função com mais de 30 linhas que contém `db.` **e** cálculos de negócio **e** `return jsonify(` ou `return render_template(`.

**Impacto:** Dificulta teste unitário; mudança em uma responsabilidade quebra as outras.

**Recomendação:** Separar em funções/classes com responsabilidade única (Model, Controller, Serializer).

**Categoria:** Refatoração estrutural

---## 11. Import Circular

**Severidade:** MEDIUM

**Sinal de detecção:** Módulo A importa módulo B, e módulo B importa módulo A. Em Python, manifesta-se como `ImportError: cannot import name X from partially initialized module`. Em Node.js, resulta em `undefined` ao usar o módulo importado. Procure por pares de imports que se referenciam mutuamente entre arquivos de rotas e models.

**Impacto:** Erros de inicialização difíceis de rastrear; impossibilidade de testar módulos isoladamente.

**Recomendação:** Extrair a dependência compartilhada para um terceiro módulo; usar injeção de dependência.

**Categoria:** Refatoração estrutural

---## 12. Queries N+1

**Severidade:** MEDIUM

**Sinal de detecção:** Um loop que, a cada iteração, executa uma query ao banco para buscar dados relacionados ao item da iteração atual — resultando em N queries adicionais para N registros. Sinais nos arquivos de código-fonte:
- Python: `for item in lista:` seguido de `db.execute(f"SELECT ... WHERE id = {item['id']}")` ou `Model.query.get(item.id)` dentro do mesmo loop.
- Node.js: `for ... of lista` ou `.forEach(` contendo `await Model.findOne(` ou `await db.query(` com valor da iteração como filtro.
- ORM sem eager loading: acesso a relações como `pedido.usuario` (SQLAlchemy) ou `order.user` (Sequelize) dentro de loop sobre lista já carregada — cada acesso dispara uma nova query.

**Impacto:** Performance degrada linearmente com o volume de dados; em produção pode gerar centenas de queries por request.

**Recomendação:** Carregar dados relacionados em uma única query com `JOIN`, `IN (...)`, ou eager loading do ORM (`joinedload`, `include`).

**Categoria:** Refatoração estrutural

---## 13. Magic Numbers / Strings sem Nome

**Severidade:** LOW

**Sinal de detecção:** Literais numéricos ou strings espalhados no código sem atribuição a uma constante nomeada. Sinais:
- `if status == 3:` sem explicar o que `3` significa.
- `time.sleep(30)` ou `max_retries = 5` embutidos em funções de negócio.
- Strings de status como `"ativo"`, `"pendente"` repetidas literalmente em múltiplos arquivos.

**Impacto:** Leitura difícil; risco de inconsistência ao alterar o valor em apenas um lugar.

**Recomendação:** Extrair para constantes nomeadas ou enum no módulo de config ou domínio.

**Categoria:** Refatoração estrutural

---## 14. Ausência de Separação de Responsabilidade de Config

**Severidade:** MEDIUM

**Sinal de detecção:** Configurações de ambiente (`DEBUG`, `DATABASE_URL`, `PORT`) espalhadas por múltiplos arquivos em vez de centralizadas em um único módulo de config (`config.py`, `settings.py`, `config/index.js`). Sinal: `os.environ.get('VAR')` ou `process.env.VAR` chamados em arquivos de rota, model ou controller — não em um único ponto de entrada de configuração.

**Impacto:** Difícil de auditar quais variáveis são necessárias; risco de divergência entre ambientes.

**Recomendação:** Centralizar toda leitura de `os.environ` / `process.env` em um módulo de config único.

**Categoria:** Refatoração estrutural

---

## APIs Deprecated por Stack

Verifique a stack detectada na Fase 1 e confira os sinais abaixo **nos arquivos de código-fonte**. Registre como finding HIGH se encontrado.

### Flask (Python)
| Onde buscar     | Sinal a procurar                        | Problema                                      |
| --------------- | --------------------------------------- | --------------------------------------------- |
| Arquivos `.py`  | `@app.before_first_request`             | Removido no Flask 2.3+; use `with app.app_context()` |
| Arquivos `.py`  | `from flask.ext.`                       | Removido no Flask 1.0; use o pacote diretamente |
| Arquivos `.py`  | `flask.escape(` ou `from flask import escape` | Movido para `markupsafe.escape` no Flask 2.0 |

### Django (Python)
| Onde buscar     | Sinal a procurar                        | Problema                                      |
| --------------- | --------------------------------------- | --------------------------------------------- |
| Arquivos `.py`  | `from django.conf.urls import url`      | `url()` removido no Django 4.0; use `path()` ou `re_path()` |
| Arquivos `.py`  | `django.utils.encoding.force_text`      | Renomeado para `force_str` no Django 4.0      |
| Arquivos `.py`  | `django.utils.translation.ugettext`     | Removido no Django 4.0; use `gettext`         |

### Express / Node.js
| Onde buscar          | Sinal a procurar                        | Problema                                      |
| -------------------- | --------------------------------------- | --------------------------------------------- |
| Arquivos `.js`/`.ts` | `app.del(`                              | Removido; use `app.delete(`                   |
| Arquivos `.js`/`.ts` | `require('url').parse(`                 | Legado; use `new URL()`                       |
| `package.json`       | `"body-parser"` como dependência separada | Já embutido no Express 4.16+; use `express.json()` |

Se a stack não estiver nesta lista, registre explicitamente no relatório: "Nenhuma API deprecated identificada para a stack `<nome>`."

**Categoria:** Refatoração estrutural
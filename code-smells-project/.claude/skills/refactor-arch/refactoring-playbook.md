# Playbook de Refatoração

Use este documento na Fase 3 para aplicar a transformação correspondente a cada finding do relatório. No campo `Recommendation` do relatório, cite o nome do padrão (ex.: "Aplicar Extração de Model").

Para cada anti-pattern do relatório, localize o padrão correspondente abaixo e siga os passos na ordem indicada. Não aplique transformações além do que o padrão descreve — escopo adicional pertence a um finding separado.

Os exemplos usam pseudocódigo agnóstico de linguagem. Aplique os idiomas e convenções da stack detectada na Fase 1.

---

## Decomposição de God File

**Anti-pattern correspondente:** #1 God File / Monolítico

**Quando aplicar:** arquivo único concentra rotas, lógica de negócio e acesso a dados.

**Passos:**
1. Identifique os domínios presentes no arquivo (ex.: produtos, pedidos, usuários).
2. Para cada domínio, extraia em ordem: Model → Controller → View/Route.
3. Aplique os padrões Extração de Model, Extração de Controller e Extração de Config conforme os problemas encontrados em cada extração.
4. Reduza o arquivo original a um entry point limpo contendo apenas registro de routers e middlewares.

**Antes:**
```pseudocode
// entry point — tudo junto
ROUTE GET /recursos:
    rows = DB.query("SELECT * FROM recursos")
    resultado = [transformar(r) for r in rows]
    return HTTP 200, resultado
```

**Depois:**
```pseudocode
// model/recurso_model
FUNCTION get_all(db):
    return db.query("SELECT * FROM recursos")

// controller/recurso_controller
FUNCTION listar(db):
    return [transformar(r) for r in recurso_model.get_all(db)]

// view/recurso_routes
ROUTE GET /recursos:
    return HTTP 200, recurso_controller.listar(db)

// entry point
REGISTER router recurso_routes
REGISTER middleware error_handler
```

---

## Extração de Controller

**Anti-pattern correspondente:** #2 Fat Route

**Quando aplicar:** handler de rota contém lógica de negócio ou cálculos de domínio.

**Passos:**
1. Mova toda lógica de negócio do handler para uma função no Controller do domínio correspondente.
2. O handler passa a extrair dados do request, chamar o controller e retornar a resposta HTTP.
3. O controller recebe dados simples (não objetos de request) e retorna dados simples (não respostas HTTP).

**Antes:**
```pseudocode
ROUTE POST /pedidos:
    itens = REQUEST.body.itens
    total = SUM(item.preco * item.qtd FOR item IN itens)
    IF total <= 0: return HTTP 400, "total inválido"
    DB.insert("pedidos", {total})
    return HTTP 201, {total}
```

**Depois:**
```pseudocode
// controller/pedido_controller
FUNCTION criar(itens, db):
    total = SUM(item.preco * item.qtd FOR item IN itens)
    IF total <= 0: RAISE erro("total inválido")
    pedido_model.inserir(total, db)
    return {total}

// view/pedido_routes
ROUTE POST /pedidos:
    resultado = pedido_controller.criar(REQUEST.body.itens, db)
    return HTTP 201, resultado
```

---

## Extração de Model

**Anti-pattern correspondente:** #3 Acesso Direto ao Banco na Rota

**Quando aplicar:** queries ao banco dentro de handlers de rota ou controllers.

**Passos:**
1. Crie ou expanda o arquivo de Model do domínio correspondente.
2. Mova cada query para uma função nomeada pelo que ela faz (ex.: `get_by_id`, `insert`, `delete`).
3. Substitua a query no local de origem pela chamada à função do Model.

**Antes:**
```pseudocode
ROUTE GET /recursos/:id:
    row = DB.query("SELECT * FROM recursos WHERE id = ?", id)
    return HTTP 200, row
```

**Depois:**
```pseudocode
// model/recurso_model
FUNCTION get_by_id(id, db):
    return db.query("SELECT * FROM recursos WHERE id = ?", id)

// view/recurso_routes
ROUTE GET /recursos/:id:
    row = recurso_model.get_by_id(REQUEST.params.id, db)
    return HTTP 200, row
```

---

## Extração de Config

**Anti-pattern correspondente:** #4 Segredo / Configuração Hardcoded e #14 Ausência de Separação de Config

**Quando aplicar:** valores de configuração ou segredos literais no código; leitura de variáveis de ambiente espalhada por múltiplos arquivos.

**Passos:**
1. Crie um módulo de config centralizado (`config/settings` ou equivalente).
2. Mova toda leitura de variável de ambiente para este módulo, com valores default apenas para desenvolvimento.
3. Substitua cada ocorrência hardcoded no código por uma referência ao módulo de config.
4. Nunca coloque o valor real do segredo no código — apenas a leitura do ambiente.

**Antes:**
```pseudocode
// entry point
APP.secret_key = "chave-hardcoded-123"
DB_URL = "db://usuario:senha@host/banco"
```

**Depois:**
```pseudocode
// config/settings
SECRET_KEY = ENV.get("SECRET_KEY", "dev-only-key")
DB_URL     = ENV.get("DATABASE_URL", "db://localhost/dev")

// entry point
IMPORT config
APP.secret_key = config.SECRET_KEY
APP.db_url     = config.DB_URL
```

---

## Query Parametrizada

**Anti-pattern correspondente:** #5 SQL Injection

**Quando aplicar:** valores externos concatenados diretamente em strings SQL.

**Passos:**
1. Localize toda construção de string SQL que interpole variáveis externas diretamente.
2. Substitua pela sintaxe de parâmetros da biblioteca de banco em uso (placeholder posicional ou nomeado).
3. Passe os valores como argumento separado da string — nunca interpolados na string.

**Antes:**
```pseudocode
valor = REQUEST.body.campo
DB.query("SELECT * FROM tabela WHERE campo = '" + valor + "'")
```

**Depois:**
```pseudocode
valor = REQUEST.body.campo
DB.query("SELECT * FROM tabela WHERE campo = ?", [valor])
```

---

## Error Handler Centralizado

**Anti-pattern correspondente:** #6 Tratamento de Erros Duplicado

**Quando aplicar:** blocos de captura de exceção com retorno de erro HTTP repetidos em múltiplos handlers.

**Passos:**
1. Crie um error handler global no módulo de middlewares.
2. Implemente a lógica de formatação de resposta de erro (status code + corpo) neste handler único.
3. Remova os blocos de tratamento genérico das rotas; mantenha apenas os que tratam casos de negócio específicos.
4. Registre o error handler global no entry point.

**Antes:**
```pseudocode
ROUTE GET /recursos:
    TRY: ...
    CATCH e: return HTTP 500, {error: e.message}

ROUTE POST /recursos:
    TRY: ...
    CATCH e: return HTTP 500, {error: e.message}
```

**Depois:**
```pseudocode
// middlewares/error_handler
FUNCTION handle(error):
    code = error.http_code IF error.http_code ELSE 500
    return HTTP code, {error: error.message}

// entry point
REGISTER middleware error_handler
```

---

## Validação de Input na Fronteira

**Anti-pattern correspondente:** #7 Ausência de Validação na Fronteira

**Quando aplicar:** dados do request usados diretamente sem verificação de presença ou tipo.

**Passos:**
1. Identifique todos os campos esperados de cada endpoint.
2. Adicione validação logo após a extração do request, antes de qualquer chamada a controller ou model.
3. Retorne HTTP 400 com mensagem descritiva para qualquer campo ausente ou com tipo inválido.
4. O controller recebe apenas dados já validados.

**Antes:**
```pseudocode
ROUTE POST /recursos:
    data = REQUEST.body
    resultado = controller.criar(data.nome, data.email)
    return HTTP 201, resultado
```

**Depois:**
```pseudocode
ROUTE POST /recursos:
    data = REQUEST.body
    IF NOT data.nome OR NOT data.email:
        return HTTP 400, {error: "nome e email são obrigatórios"}
    resultado = controller.criar(data.nome, data.email)
    return HTTP 201, resultado
```

---

## Eliminação de Estado Global Mutável

**Anti-pattern correspondente:** #8 Estado Global Mutável

**Quando aplicar:** variável de módulo mutável escrita durante o ciclo de vida da aplicação.

**Passos:**
1. Identifique a variável global mutável e os endpoints que a escrevem.
2. Se os dados devem persistir entre requests: mova para o banco de dados usando o Model correspondente.
3. Se os dados são transitórios (cache, sessão): use mecanismo externo adequado (cache, sessão do framework).
4. Remova a declaração da variável global.

**Antes:**
```pseudocode
// módulo raiz
recursos = []

ROUTE POST /recursos:
    recursos.APPEND(REQUEST.body)
    return HTTP 201, REQUEST.body
```

**Depois:**
```pseudocode
// model/recurso_model
FUNCTION inserir(dados, db):
    db.insert("recursos", dados)
    return dados

// view/recurso_routes
ROUTE POST /recursos:
    resultado = recurso_model.inserir(REQUEST.body, db)
    return HTTP 201, resultado
```

---

## Injeção de Dependência

**Anti-pattern correspondente:** #9 Acoplamento Forte / Ausência de Injeção de Dependência

**Quando aplicar:** controller ou rota instancia ou importa diretamente uma dependência de infraestrutura.

**Passos:**
1. Mova a criação da dependência (conexão ao banco, cliente HTTP) para o entry point ou para o Config.
2. Passe a dependência como parâmetro para as funções que a utilizam.
3. O controller não deve instanciar nem importar módulos de infraestrutura diretamente.

**Antes:**
```pseudocode
// controller/recurso_controller
db = DB.connect("banco.db")   // instancia dependência internamente

FUNCTION listar():
    return db.query("SELECT * FROM recursos")
```

**Depois:**
```pseudocode
// controller/recurso_controller
FUNCTION listar(db):           // dependência injetada pelo caller
    return recurso_model.get_all(db)

// entry point
db = DB.connect(config.DB_URL)
APP.locals.db = db
```

---

## Separação de Responsabilidades

**Anti-pattern correspondente:** #10 Violação de SRP

**Quando aplicar:** função ou classe executa ao mesmo tempo acesso a dados, regra de negócio e formatação de resposta.

**Passos:**
1. Identifique os grupos de responsabilidade presentes na função/classe (acesso a dados, lógica de negócio, serialização).
2. Para cada grupo, mova o código para a camada correspondente conforme `architecture-guidelines.md`: queries → Model, regras → Controller, serialização → View/Route.
3. A função original passa a orquestrar chamadas entre as camadas, sem conter implementação de nenhuma delas.

**Antes:**
```pseudocode
FUNCTION processar_pedido(id, db):
    // acesso a dados
    pedido = db.query("SELECT * FROM pedidos WHERE id = ?", id)
    // regra de negócio
    desconto = pedido.total * 0.1 IF pedido.tipo == "vip" ELSE 0
    // formatação
    return {id: pedido.id, total: pedido.total - desconto, desconto: desconto}
```

**Depois:**
```pseudocode
// model/pedido_model
FUNCTION get_by_id(id, db):
    return db.query("SELECT * FROM pedidos WHERE id = ?", id)

// controller/pedido_controller
FUNCTION calcular_desconto(pedido):
    return pedido.total * 0.1 IF pedido.tipo == "vip" ELSE 0

// view/pedido_routes
ROUTE GET /pedidos/:id:
    pedido  = pedido_model.get_by_id(REQUEST.params.id, db)
    desconto = pedido_controller.calcular_desconto(pedido)
    return HTTP 200, {id: pedido.id, total: pedido.total - desconto, desconto: desconto}
```

---

## Quebra de Ciclo de Importação

**Anti-pattern correspondente:** #11 Import Circular

**Quando aplicar:** módulo A importa módulo B e módulo B importa módulo A, causando erro de inicialização.

**Passos:**
1. Identifique o par de módulos que se importam mutuamente.
2. Extraia o símbolo compartilhado (função, classe, constante) para um terceiro módulo independente.
3. Ambos os módulos originais passam a importar do terceiro módulo — nenhum importa o outro.
4. Se a dependência circular surgiu de um controller importando uma rota ou vice-versa, aplique o padrão Injeção de Dependência para eliminar a causa raiz.

**Antes:**
```pseudocode
// module_a
IMPORT module_b
FUNCTION usar_b(): return module_b.funcao()

// module_b
IMPORT module_a           // ciclo: b depende de a, a depende de b
FUNCTION funcao(): return module_a.valor
```

**Depois:**
```pseudocode
// module_shared  (novo módulo independente)
valor = "compartilhado"

// module_a
IMPORT module_shared
FUNCTION usar_b(): return module_shared.valor

// module_b
IMPORT module_shared
FUNCTION funcao(): return module_shared.valor
```

---

## Query Unificada

**Anti-pattern correspondente:** #12 Queries N+1

**Quando aplicar:** loop que executa uma query por iteração para buscar dados relacionados.

**Passos:**
1. Identifique o par loop + query que gera o N+1.
2. Substitua por uma única query com JOIN ou WHERE IN que traga todos os dados necessários de uma vez.
3. Se usar ORM com lazy loading, configure eager loading explícito para a relação em questão.

**Antes:**
```pseudocode
registros = DB.query("SELECT * FROM pedidos")
FOR pedido IN registros:
    // N queries adicionais
    usuario = DB.query("SELECT * FROM usuarios WHERE id = ?", pedido.usuario_id)
```

**Depois:**
```pseudocode
registros = DB.query("""
    SELECT pedidos.*, usuarios.nome AS usuario_nome
    FROM pedidos
    JOIN usuarios ON usuarios.id = pedidos.usuario_id
""")
```

---

## Extração de Constantes

**Anti-pattern correspondente:** #13 Magic Numbers / Strings sem Nome

**Quando aplicar:** literais numéricos ou strings com significado de domínio espalhados pelo código.

**Passos:**
1. Identifique cada literal que representa um conceito de domínio (status, limite, código).
2. Declare-o como constante nomeada no módulo de config ou em um módulo de constantes do domínio.
3. Substitua todas as ocorrências pela referência à constante.

**Antes:**
```pseudocode
IF pedido.status == 3: ...
IF COUNT(itens) > 50: ...
```

**Depois:**
```pseudocode
// config/constants
STATUS_ENTREGUE      = 3
MAX_ITENS_POR_PEDIDO = 50

// uso
IF pedido.status == STATUS_ENTREGUE: ...
IF COUNT(itens) > MAX_ITENS_POR_PEDIDO: ...
```

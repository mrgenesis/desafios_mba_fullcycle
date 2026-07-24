# Guidelines de Arquitetura MVC

Use este documento na Fase 3 para aplicar a estrutura de pastas e as regras de responsabilidade de cada camada. A estrutura é agnóstica de stack — aplique as convenções de nomenclatura e os idiomas da linguagem detectada na Fase 1.

---

## Camadas da arquitetura alvo

A arquitetura alvo é baseada no padrão **MVC** estendido com duas camadas de suporte necessárias em aplicações web reais:

| Camada | Parte do MVC? | Papel |
| ------ | ------------- | ----- |
| Model | ✅ Sim | Dados e persistência |
| View / Routes | ✅ Sim | Roteamento HTTP e formatação de resposta |
| Controller | ✅ Sim | Lógica de negócio |
| Config | ❌ Suporte | Centraliza configuração e variáveis de ambiente |
| Middlewares | ❌ Suporte | Pipeline de request/response transversal |

Config e Middlewares não fazem parte do MVC clássico. São adicionados porque frameworks web operam sobre um ciclo HTTP que exige esses pontos de intercepção. Tratá-los como camadas separadas evita que se misturem ao Controller (violação de SRP) ou ao entry point (God File).

---

## Responsabilidades por camada

### Config
**Pertence aqui:** leitura de variáveis de ambiente, valores default para desenvolvimento, parâmetros de conexão a serviços externos.

**Nunca:** lógica de negócio, definições de rota, queries ao banco.

---

### Model
**Pertence aqui:** definição de schema ou classe ORM, funções de acesso a dados (queries, inserts, updates, deletes), validações a nível de persistência.

**Nunca:** regras de negócio, cálculos de domínio, formatação de resposta HTTP, imports do framework web.

---

### Controller
**Pertence aqui:** lógica de negócio, validações de domínio, chamadas às funções do Model, retorno de objetos de dados simples (não de respostas HTTP).

**Nunca:** queries diretas ao banco, definições de rota, construção de respostas HTTP (status codes, serialização).

---

### View / Routes
**Pertence aqui:** mapeamento de URL e método HTTP ao controller correspondente, extração de dados do request (body, params, query string), conversão do retorno do controller em resposta HTTP.

**Nunca:** lógica de negócio, queries ao banco, cálculos de domínio.

---

### Middlewares
**Pertence aqui:** error handler global, autenticação e autorização transversais, logging de requests, headers globais (CORS etc.).

**Nunca:** lógica de negócio específica de um domínio.

---

### Entry point
**Pertence aqui:** criação da instância da aplicação, registro de routers ou blueprints, registro de middlewares globais, inicialização da conexão com o banco a partir do Config.

**Nunca:** lógica de negócio, queries, definições de rota além do registro de routers.

---

## Estrutura de pastas alvo

```
<raiz>/
├── config/            # Config
├── models/            # Models (um arquivo por entidade de domínio)
├── controllers/       # Controllers (um arquivo por domínio)
├── views/ ou routes/  # Views / Routes (um arquivo por domínio)
├── middlewares/       # Middlewares
└── <entry-point>      # Entry point (nome idiomático da stack)
```

Aplique a nomenclatura de arquivos e classes conforme os idiomas da linguagem detectada na Fase 1.

---

## Checklist de validação da estrutura

Confirme cada item antes de declarar a Fase 3 concluída:

| Critério | O que verificar |
| -------- | --------------- |
| Config isolada | Nenhuma leitura de variável de ambiente fora de `config/` |
| Models sem HTTP | Nenhum import do framework web em `models/` |
| Controllers sem HTTP | Nenhuma construção de resposta HTTP em `controllers/` |
| Views sem lógica | Nenhuma query ao banco e nenhum cálculo de negócio em `views/` ou `routes/` |
| Error handler único | Nenhum tratamento de erro HTTP fora de `middlewares/` |
| Entry point limpo | Entry point contém apenas registro de routers/blueprints e middlewares |

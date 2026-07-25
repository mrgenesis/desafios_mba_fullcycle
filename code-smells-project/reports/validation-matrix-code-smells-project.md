# Matriz de Validação — code-smells-project

Baseline capturado em 2026-07-24 com `seed.py` (IDs fixos) contra a aplicação
original, executando `reports/fixtures-code-smells-project.sh` nesta ordem.
Corpo completo das respostas de baseline em `reports/baseline-code-smells-project.txt`.

Nota sobre não-determinismo: o campo `criado_em` de registros criados
dinamicamente pelas próprias fixtures (pedido id=2) reflete o horário real de
execução e varia entre a captura do baseline e a validação pós-refatoração —
não deve ser usado como critério de reprovação. Todo o restante do corpo da
resposta deve ser comparado byte a byte.

| # | Fixture (método + rota + payload) | IDs do seed | Baseline (capturado) | Esperado pós-refatoração | Fonte |
|---|---|---|---|---|---|
| 1 | GET /health | — | 200, inclui `secret_key` e `debug` no corpo | 200, sem os campos `secret_key` e `debug`; demais campos idênticos | Correção obrigatória — Segredo Hardcoded |
| 2 | GET /produtos | produto.id=1,2 | 200, lista com os 2 produtos seed | idêntico ao baseline | Refatoração estrutural |
| 3 | GET /produtos/1 | produto.id=1 | 200 `{"dados":{"id":1,"nome":"Produto Seed A",...}}` | idêntico ao baseline | Refatoração estrutural |
| 4 | GET /produtos/999 | — | 404 `{"erro":"Produto não encontrado","sucesso":false}` | idêntico ao baseline | Refatoração estrutural |
| 5 | GET /produtos/busca?q=Seed | produto.id=1,2 | 200, 2 produtos, total=2 | idêntico ao baseline | Refatoração estrutural (Query Parametrizada aplicada sem mudar contrato) |
| 6 | GET /produtos/busca?preco_min=abc | — | 500 `{"erro":"could not convert string to float: 'abc'"}` | 400 com corpo contendo chave `erro` (mensagem pode variar, ex.: `{"erro":"preco_min inválido"}`) | Correção obrigatória — Ausência de Validação na Fronteira |
| 7 | POST /produtos {"nome":"Produto Fixture","preco":10.5,"estoque":3,"categoria":"informatica"} | — | 201 `{"dados":{"id":3},"mensagem":"Produto criado","sucesso":true}` | idêntico ao baseline | Refatoração estrutural |
| 8 | POST /produtos {"nome":"Produto Sem Preco","estoque":3} | — | 400 `{"erro":"Preço é obrigatório"}` | idêntico ao baseline | Refatoração estrutural |
| 9 | PUT /produtos/1 (update completo) | produto.id=1 | 200 `{"mensagem":"Produto atualizado","sucesso":true}` | idêntico ao baseline | Refatoração estrutural |
| 10 | DELETE /produtos/2 | produto.id=2 | 200 `{"mensagem":"Produto deletado","sucesso":true}` | idêntico ao baseline | Refatoração estrutural |
| 11 | GET /usuarios | usuario.id=1,2 | 200, cada usuário inclui o campo `senha` em texto plano | 200, mesmos usuários, **sem** o campo `senha` | Correção obrigatória — Senha em texto plano exposta via API |
| 12 | GET /usuarios/1 | usuario.id=1 | 200, inclui `senha":"senha123"` | 200, sem o campo `senha` | Correção obrigatória — Senha em texto plano exposta via API |
| 13 | POST /usuarios {"nome":"Fixture User","email":"fixture@example.com","senha":"abc123"} | — | 201 `{"dados":{"id":3},"sucesso":true}` | idêntico ao baseline (senha passa a ser armazenada com hash internamente, resposta não muda) | Refatoração de implementação sem mudança de contrato |
| 14 | POST /login {"email":"seed@example.com","senha":"senha123"} | usuario.id=1 | 200, login OK | idêntico ao baseline | Refatoração de implementação sem mudança de contrato |
| 15 | POST /login {"email":"seed@example.com","senha":"errada"} | usuario.id=1 | 401 `{"erro":"Email ou senha inválidos","sucesso":false}` | idêntico ao baseline | Refatoração de implementação sem mudança de contrato |
| 16 | POST /login {"email":"' OR '1'='1' -- ","senha":"qualquer"} | — | **200**, autentica como usuario.id=1 sem senha válida (bypass) | 401 `{"erro":"Email ou senha inválidos","sucesso":false}` — igual à linha 15 | Correção obrigatória — SQL Injection |
| 17 | POST /pedidos {"usuario_id":1,"itens":[{"produto_id":1,"quantidade":1}]} | usuario.id=1, produto.id=1 | 201 `{"dados":{"pedido_id":2,"total":120.0},...}` | idêntico ao baseline | Refatoração estrutural |
| 18 | GET /pedidos | pedido.id=1,2 | 200, 2 pedidos (ver nota de não-determinismo para `criado_em` do pedido id=2) | idêntico ao baseline, exceto `criado_em` do pedido id=2 | Refatoração estrutural |
| 19 | GET /pedidos/usuario/1 | usuario.id=1 | 200, mesmos 2 pedidos (ver nota de não-determinismo) | idêntico ao baseline, exceto `criado_em` do pedido id=2 | Refatoração estrutural (resolve também N+1 do carregamento de itens) |
| 20 | PUT /pedidos/1/status {"status":"aprovado"} | pedido.id=1 | 200 `{"mensagem":"Status atualizado","sucesso":true}` | idêntico ao baseline | Refatoração estrutural |
| 21 | GET /relatorios/vendas | — | 200, faturamento_bruto=220.0, ticket_medio=110.0 | idêntico ao baseline | Refatoração estrutural (SRP) |
| 22 | POST /admin/query {"sql":"SELECT COUNT(*) FROM produtos"} | — | **200**, executa o SQL do payload e retorna o resultado | 404 (rota removida — não deve mais existir nem aceitar SQL do cliente) | Correção obrigatória — Acesso Direto ao Banco na Rota |
| 23 | POST /admin/reset-db (sem autenticação) | — | **200**, apaga todas as tabelas | 401/403 sem autenticação de administrador válida | Correção obrigatória — Acesso Direto ao Banco na Rota |

Total: 23 fixtures | 7 com mudança de comportamento obrigatória (linhas 1, 6, 11, 12, 16, 22, 23) | 16 idênticas ao baseline.

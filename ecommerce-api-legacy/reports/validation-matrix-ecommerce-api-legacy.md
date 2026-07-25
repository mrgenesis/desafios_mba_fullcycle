# Matriz de Validação — ecommerce-api-legacy

Banco SQLite em memória (`:memory:`), recriado do zero a cada boot com o
mesmo seed fixo (`AppManager.initDb()`): user id=1 "Leonan", courses id=1
"Clean Architecture" (997.00) e id=2 "Docker" (497.00), enrollment id=1
(user 1, course 1), payment id=1 (997.00, PAID). Como o processo sempre
recomeça do zero, IDs subsequentes gerados pelas fixtures são determinísticos
desde que a ordem das requisições seja sempre a mesma
(`reports/fixtures-ecommerce-api-legacy.sh`). Baseline completo em
`reports/baseline-ecommerce-api-legacy.txt`.

| # | Fixture (método + rota + payload) | IDs do seed | Baseline (capturado) | Esperado pós-refatoração | Fonte |
|---|---|---|---|---|---|
| 1 | POST /api/checkout {usr:Leonan,eml:leonan@fullcycle.com.br,pwd:123,c_id:1,card:4111...} | user.id=1, course.id=1 | 200 `{"msg":"Sucesso","enrollment_id":2}` | idêntico ao baseline | Refatoração estrutural |
| 2 | POST /api/checkout {usr:"Nova Pessoa",eml:nova@example.com,c_id:2,card:4111...} **sem pwd** | course.id=2 | 200 `{"msg":"Sucesso","enrollment_id":3}` (usuário criado com senha padrão "123456") | 400, corpo indicando que a senha é obrigatória | Correção obrigatória — Ausência de Validação na Fronteira / senha padrão fraca |
| 3 | POST /api/checkout {usr:"Outra Pessoa",eml:outra@example.com,pwd:abc,c_id:1,card:5111...} | course.id=1 | 400 texto `Pagamento recusado` | idêntico ao baseline | Refatoração estrutural |
| 4 | POST /api/checkout {usr:"Mais Uma",...,c_id:999,card:4111...} | — | 404 texto `Curso não encontrado` | idêntico ao baseline | Refatoração estrutural |
| 5 | POST /api/checkout {usr:"Sem Curso",...} **sem c_id** | — | 400 texto `Bad Request` | idêntico ao baseline | Refatoração estrutural |
| 6 | GET /api/admin/financial-report (antes do delete) | — | 200 `[{"course":"Clean Architecture","revenue":1994,"students":[{"student":"Leonan","paid":997},{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":497,"students":[{"student":"Nova Pessoa","paid":497}]}]` | 200 `[{"course":"Clean Architecture","revenue":1994,"students":[{"student":"Leonan","paid":997},{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":0,"students":[]}]` — Docker fica sem matrícula porque a fixture 2 (que a criava) agora é corretamente rejeitada com 400; efeito em cascata esperado da correção da linha 2, não uma regressão | Refatoração estrutural (resolve N+1 internamente) + efeito em cascata da correção obrigatória da linha 2 |
| 7 | DELETE /api/users/1 | user.id=1 | 200 texto `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` | 200, texto de sucesso sem menção a dados órfãos (ex.: `Usuário deletado com sucesso.`); enrollments e payments do usuário 1 devem ser removidos em cascata | Correção obrigatória — Exclusão de usuário deixa dados órfãos |
| 8 | GET /api/admin/financial-report (depois do delete) | — | 200, curso "Clean Architecture" mostra 2 alunos `"Unknown"` com revenue 1994 (dados órfãos) | 200 `[{"course":"Clean Architecture","revenue":0,"students":[]},{"course":"Docker","revenue":0,"students":[]}]` — sem entradas órfãs (Docker permanece em 0 pelo mesmo motivo da linha 6) | Correção obrigatória — Exclusão de usuário deixa dados órfãos |
| 9 | DELETE /api/users/999 (inexistente) | — | 200 texto `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` | 200, mesmo texto de sucesso genérico usado na linha 7 (comportamento sem checagem de existência preservado) | Refatoração estrutural |
| 10 | Log do console durante POST /api/checkout | — | `paymentGatewayKey` completa impressa em texto plano no console a cada checkout | console não deve mais imprimir a chave do gateway de pagamento (validado por inspeção de código/log, não por corpo de resposta HTTP) | Correção obrigatória — Segredo Hardcoded |
| 11 | Algoritmo de hash da senha armazenada | — | `badCrypto()` (determinística, sem sal) | `bcrypt` (não determinística, com sal) — não observável via HTTP pois a senha nunca é retornada; validado por inspeção de código | Correção obrigatória — Hashing de senha inseguro |

Total: 11 linhas | 5 com mudança de comportamento obrigatória (linhas 2, 7, 8, 10, 11) | 6 idênticas ao baseline.

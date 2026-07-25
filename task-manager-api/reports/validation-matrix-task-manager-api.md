# Matriz de Validação — task-manager-api

Seed via `seed.py` (não modificado): users id=1 João/admin, id=2 Maria/user,
id=3 Pedro/manager; categories id=1..4; tasks id=1..10, com overdue
determinístico para as tasks id=1 e id=4 (due_date no passado, status
"pending"). Baseline completo em `reports/baseline-task-manager-api.txt`.

Nota sobre não-determinismo: os campos `created_at`, `updated_at`, `due_date`,
`generated_at` e `days_overdue` refletem o horário real de execução do seed/
requisição e variam em segundos entre a captura do baseline e a validação
pós-refatoração — não usar como critério de reprovação. O campo derivado
`overdue` (booleano) deve permanecer estável, pois os offsets do seed são em
dias.

| # | Fixture (método + rota + payload) | Baseline (capturado) | Esperado pós-refatoração | Fonte |
|---|---|---|---|---|
| 1 | GET /users | 200, lista sem campo `password` (get_users já não o inclui) | idêntico ao baseline | Refatoração estrutural |
| 2 | GET /users/1 | 200, inclui `"password":"81dc9bdb52d04dc20036dbd8313ed055"` (hash MD5) | 200, sem o campo `password`; demais campos e `tasks` aninhadas idênticos | Correção obrigatória — Hashing de senha inseguro e senha exposta via API |
| 3 | POST /login {email:joao@email.com,password:1234} | 200, `user` inclui campo `password` (hash MD5) | 200, `user` sem o campo `password`; `message` e `token` mantidos | Correção obrigatória — Hashing de senha inseguro e senha exposta via API |
| 4 | POST /login {email:joao@email.com,password:errada} | 401 `{"error":"Credenciais inválidas"}` | idêntico ao baseline (login continua validando com sucesso via hash, agora seguro) | Refatoração estrutural |
| 5 | GET /users/1/tasks | 200, 4 tasks, `overdue` true para id=1 e id=4 | idêntico ao baseline (mesmos valores de `overdue`) | Refatoração estrutural (usa fonte única de verdade para overdue) |
| 6 | GET /tasks | 200, 10 tasks com `user_name`/`category_name` resolvidos | idêntico ao baseline | Refatoração estrutural (resolve N+1 internamente) |
| 7 | GET /tasks/1 | 200, `overdue: true` | idêntico ao baseline | Refatoração estrutural |
| 8 | GET /tasks/search?q=bug | 200, 1 task ("Corrigir bug no filtro de busca") | idêntico ao baseline | Refatoração estrutural |
| 9 | GET /tasks/search?priority=abc | **500**, página HTML do Werkzeug Debugger (`ValueError: invalid literal for int()`) | 400, corpo JSON indicando prioridade inválida | Correção obrigatória — Ausência de Validação na Fronteira |
| 10 | GET /tasks/stats | 200 `{"total":10,"pending":6,"in_progress":2,"done":1,"cancelled":1,"overdue":2,"completion_rate":10.0}` | idêntico ao baseline | Refatoração estrutural |
| 11 | GET /reports/summary | 200, `overdue.count:2`, `overview.total_tasks:10`, etc. | idêntico ao baseline (exceto `generated_at`/`due_date`/`days_overdue`, não-determinísticos) | Refatoração estrutural |
| 12 | GET /reports/user/1 | 200, `statistics.overdue:2`, `total_tasks:4` | idêntico ao baseline | Refatoração estrutural |
| 13 | GET /categories | 200, 4 categorias | idêntico ao baseline | Refatoração estrutural |
| 14 | PUT /categories/1 (corpo JSON `null`) | **500**, página HTML do Werkzeug Debugger (`AttributeError`/`TypeError` em `'name' in data`) | 400 `{"error":"Dados inválidos"}` (mesmo padrão dos demais endpoints de escrita) | Correção obrigatória — Ausência de Validação na Fronteira |
| 15 | POST /tasks {title,description,status,priority,user_id:1,category_id:1} | 201, `id:11` | idêntico ao baseline | Refatoração estrutural |
| 16 | PUT /tasks/1 {status:done} | 200, `status:"done"` | idêntico ao baseline | Refatoração estrutural |
| 17 | DELETE /tasks/2 | 200 `{"message":"Task deletada com sucesso"}` | idêntico ao baseline | Refatoração estrutural |
| 18 | SECRET_KEY e credenciais SMTP hardcoded | literais no código-fonte | lidas de variável de ambiente (dev default apenas local); não observável via HTTP | Correção obrigatória — Credenciais Hardcoded (validado por inspeção de código) |
| 19 | `Model.query.get(id)` (SQLAlchemy) | API legada | `db.session.get(Model, id)`; não observável via HTTP | Refatoração estrutural — API Deprecated (validado por inspeção de código) |

Total: 19 linhas | 4 com mudança de comportamento obrigatória (linhas 2, 3, 9, 14) | 13 idênticas ao baseline | 2 validadas por inspeção de código (linhas 18, 19).

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   12 analyzed | ~1050 lines of code
Date:    2026-07-25

--------------------------------
Summary
--------------------------------
CRITICAL : 2
HIGH     : 2
MEDIUM   : 4
LOW      : 2
TOTAL    : 10 findings

--------------------------------
Findings
--------------------------------

[CRITICAL] Credenciais Hardcoded
File:            app.py:13;services/notification_service.py:7-10
Description:     app.config['SECRET_KEY'] = 'super-secret-key-123' hardcoded
                 em app.py:13. NotificationService define email_host, email_port,
                 email_user ('taskmanager@gmail.com') e email_password
                 ('senha123') como atributos literais no construtor.
Impact:          Segredos versionados no repositório; credenciais de e-mail
                 expostas permitiriam envio de e-mail em nome do serviço por
                 qualquer pessoa com acesso ao código.
Recommendation:  Ler SECRET_KEY e as credenciais SMTP de variáveis de ambiente,
                 com valores default apenas para desenvolvimento local.
Category:        Correção obrigatória
Behavior change: Nenhum endpoint expõe esses valores diretamente na resposta
                 HTTP; a mudança é apenas na origem da configuração (variável
                 de ambiente em vez de literal), sem alterar o corpo de nenhuma
                 resposta.

[CRITICAL] Hashing de senha inseguro e senha exposta via API
File:            models/user.py:16-25;29;32
Description:     set_password() (linha 29) usa hashlib.md5() — sem sal,
                 rápido e quebrado para senhas — e check_password() (linha 32)
                 compara o mesmo hash. to_dict() (linhas 16-25) inclui o campo
                 "password" (o hash MD5) na serialização, retornado
                 literalmente por GET /users, GET /users/<id>, POST /users,
                 PUT /users/<id> e POST /login.
Impact:          MD5 é reversível via rainbow table/força bruta em escala; um
                 vazamento do banco ou até uma simples chamada GET /users
                 expõe hashes de senha de todos os usuários que um atacante
                 pode quebrar offline.
Recommendation:  Usar werkzeug.security.generate_password_hash/check_password_hash
                 (bcrypt/scrypt); remover o campo password de toda serialização
                 de resposta.
Category:        Correção obrigatória
Behavior change: Antes — GET /users/1 retorna o campo "password" com o hash MD5.
                 Depois — GET /users/1 não inclui mais o campo "password" na
                 resposta (mesmo comportamento para POST /users, PUT /users/<id>
                 e o campo "user" dentro de POST /login).

[HIGH] Lógica de negócio nas Routes; ausência de Controllers
File:            routes/task_routes.py:11-299;routes/user_routes.py:10-212
Description:     As rotas executam queries diretamente (Task.query.filter_by,
                 User.query.get), validam regras de negócio (status, priority,
                 formato de e-mail, tamanho de senha) e serializam a resposta —
                 tudo no mesmo handler, sem Controller intermediário.
Impact:          Impossível reutilizar ou testar a lógica de negócio isolada da
                 camada HTTP; qualquer regra de negócio só pode ser exercitada
                 fazendo uma requisição HTTP completa.
Recommendation:  Extrair Controllers por domínio (task, user, category) que
                 recebam dados já extraídos do request e devolvam dados
                 simples, conforme architecture-guidelines.md.
Category:        Refatoração estrutural

[MEDIUM] Código duplicado: lógica de "overdue" repetida
File:            routes/task_routes.py:30-39;71-80;284-287;routes/user_routes.py:171-180;routes/report_routes.py:34-37;132-135
Description:     O bloco `if t.due_date and t.due_date < datetime.utcnow() and
                 status not in ('done','cancelled')` é reescrito em 6 lugares
                 diferentes. O método Task.is_overdue() (models/task.py:50-60)
                 implementa a mesma regra mas não é chamado por nenhuma rota —
                 código morto que deveria ser a única fonte de verdade.
Impact:          Uma mudança na regra de "atraso" (ex.: considerar também
                 status 'archived') exige edição em 6 pontos; risco de
                 divergência entre eles.
Recommendation:  Remover as reimplementações e usar Task.is_overdue() (ou
                 movê-la para o Controller) como única fonte de verdade.
Category:        Refatoração estrutural

[MEDIUM] Queries N+1 em GET /tasks
File:            routes/task_routes.py:41-57
Description:     Para cada task retornada (loop principal, linha 16), busca-se
                 User.query.get(t.user_id) (linha 42) e Category.query.get(t.category_id)
                 (linha 51) dentro do mesmo loop — duas queries adicionais por
                 task.
Impact:          Com N tasks, gera 1 + 2N queries; performance degrada
                 linearmente com o volume de dados.
Recommendation:  Usar eager loading do SQLAlchemy (joinedload em User e
                 Category) ou uma única query com JOIN.
Category:        Refatoração estrutural

[MEDIUM] Ausência de Validação na Fronteira
File:            routes/task_routes.py:260-264;routes/report_routes.py:196-202
Description:     search_tasks() converte priority e user_id com int(...) sem
                 tratamento de exceção (linhas 261;264) — um valor não numérico
                 gera 500 em vez de 400. update_category() acessa 'name' in data
                 (linha 197) sem checar antes se data é None — um PUT
                 /categories/<id> sem corpo JSON gera 500 com página HTML
                 padrão do Flask em vez de um erro JSON consistente.
Impact:          Input inválido do cliente gera erro 500 (com stack trace/HTML
                 exposto) em vez de 400 com mensagem clara.
Recommendation:  Validar tipo antes da conversão em search_tasks(); adicionar
                 checagem `if not data` em update_category() como já existe nos
                 demais handlers de escrita.
Category:        Correção obrigatória
Behavior change: Antes — GET /tasks/search?priority=abc retorna 500 (exceção
                 não tratada). Depois — retorna 400 com corpo JSON indicando
                 parâmetro inválido.
                 Antes — PUT /categories/1 sem corpo retorna 500 (HTML do Flask).
                 Depois — retorna 400 {"error": "Dados inválidos"} (mesmo padrão
                 já usado pelos outros endpoints de escrita).

[MEDIUM] Token JWT falso sem autenticação real
File:            routes/user_routes.py:210
Description:     'token': 'fake-jwt-token-' + str(user.id) — o login retorna um
                 token previsível (basta saber o id do usuário) e não validável
                 por nenhum middleware; nenhuma rota exige esse token para
                 responder.
Impact:          A API não possui autenticação real; qualquer cliente pode
                 chamar qualquer endpoint sem token válido, e o token retornado
                 não protege nada.
Recommendation:  Emitir um JWT real (assinado com SECRET_KEY vindo de config) e
                 adicionar um middleware de autenticação que valide o token nas
                 rotas que exigem usuário autenticado.
Category:        Refatoração estrutural

[LOW] Service instanciado mas nunca utilizado
File:            services/notification_service.py:1-48
Description:     NotificationService implementa envio de e-mail e notificações
                 mas não é importado nem instanciado em nenhuma rota do
                 projeto.
Impact:          Código morto sem clareza se foi removido intencionalmente;
                 aumenta a superfície de manutenção sem benefício.
Recommendation:  Remover se não fizer parte do roadmap, ou integrar
                 explicitamente ao fluxo de criação/atribuição de tasks.
Category:        Refatoração estrutural

[LOW] Imports não utilizados
File:            routes/task_routes.py:7;app.py:7
Description:     import json, os, sys, time em task_routes.py — nenhum desses
                 módulos é usado no arquivo. import os, sys, json em app.py —
                 apenas datetime (também na mesma linha) é efetivamente
                 utilizado, em health().
Impact:          Ruído de leitura; sugere copy-paste entre arquivos sem
                 limpeza.
Recommendation:  Remover os imports não utilizados.
Category:        Refatoração estrutural

--------------------------------
Deprecated APIs
--------------------------------
Stack verificada: Python + Flask 3.0.0

Não foram encontrados usos de @app.before_first_request, from flask.ext. ou
flask.escape()/from flask import escape (Flask). Porém:

[HIGH] API Deprecated: Query.get() do SQLAlchemy
File:        routes/task_routes.py:67;158;227;routes/user_routes.py:29;94;136;155;routes/report_routes.py:105;192;213
Description: User.query.get(id) / Task.query.get(id) / Category.query.get(id)
             usam a API legada Query.get(), removida do padrão recomendado a
             partir do SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1 em favor de
             db.session.get(Model, id).
Category:    Refatoração estrutural

--------------------------------
Total: 10 findings | CRITICAL: 2 | HIGH: 2 | MEDIUM: 4 | LOW: 2
================================
```

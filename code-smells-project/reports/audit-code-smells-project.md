```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code
Date:    2026-07-24

--------------------------------
Summary
--------------------------------
CRITICAL : 4
HIGH     : 2
MEDIUM   : 3
LOW      : 2
TOTAL    : 11 findings

--------------------------------
Findings
--------------------------------

[CRITICAL] God File / Monolítico
File:            app.py:1-89;controllers.py:1-293;models.py:1-315;database.py:1-87
Description:     A aplicação inteira vive em 4 arquivos soltos na raiz, sem nenhuma
                 subpasta models/, controllers/ ou routes/. app.py mistura definição
                 de rotas com acesso direto ao banco nas rotas /admin/reset-db e
                 /admin/query (linhas 47-78). models.py mistura acesso a dados com
                 regra de negócio em relatorio_vendas() (linhas 235-273).
Impact:          Qualquer mudança de regra de negócio ou de schema exige tocar em
                 múltiplos arquivos sem fronteira clara de responsabilidade;
                 impossível testar camadas isoladamente.
Recommendation:  Separar em camadas MVC (config/, models/, controllers/, routes/)
                 conforme architecture-guidelines.md.
Category:        Refatoração estrutural

[CRITICAL] Segredo / Configuração Hardcoded
File:            app.py:7-8;controllers.py:285-290
Description:     app.config["SECRET_KEY"] = "minha-chave-super-secreta-123" hardcoded
                 em app.py:7. O mesmo valor é reexposto na resposta JSON de
                 GET /health (controllers.py:289 "secret_key": "minha-chave-super-secreta-123"),
                 junto com "debug": True (controllers.py:288).
Impact:          Segredo versionado no repositório e adicionalmente vazado via API
                 pública; qualquer cliente que chame /health obtém a SECRET_KEY.
Recommendation:  Ler SECRET_KEY de variável de ambiente com fallback apenas para dev
                 local; remover secret_key e debug do payload de /health.
Category:        Correção obrigatória
Behavior change: Antes — GET /health retorna 200 com os campos "secret_key" e "debug"
                 no corpo da resposta.
                 Depois — GET /health retorna 200 sem os campos "secret_key" e "debug"
                 (mantém status, database, counts, versao).

[CRITICAL] SQL Injection
File:            models.py:28;47-50;57-61;68;92;109-111;126-129;140;148-151;155;157-161;163-166;174;188;192;220;224;279-281;289-297
Description:     Praticamente todas as funções de acesso a dados em models.py montam
                 SQL por concatenação de string com valores do request, sem
                 parâmetros (?, :param). Exemplos: get_produto_por_id (linha 28)
                 "SELECT * FROM produtos WHERE id = " + str(id); login_usuario
                 (linhas 109-111) concatena email e senha direto na cláusula WHERE;
                 buscar_produtos (linhas 289-297) concatena termo de busca em LIKE.
Impact:          Qualquer cliente pode ler, alterar ou apagar dados arbitrários do
                 banco, incluindo bypass de autenticação via injeção na query de
                 login_usuario.
Recommendation:  Usar sempre queries parametrizadas com placeholder "?" do sqlite3
                 em todas as funções listadas.
Category:        Correção obrigatória
Behavior change: Antes — POST /login com email = "' OR '1'='1' -- " retorna 200 e
                 autentica sem senha válida.
                 Depois — mesmo payload retorna 401 {"erro": "Email ou senha inválidos"}.
                 Antes — GET /produtos/busca?q='%20UNION%20SELECT... é executado
                 literalmente contra o banco.
                 Depois — o termo é tratado como valor de parâmetro literal, nunca
                 como SQL.

[CRITICAL] Acesso Direto ao Banco na Rota (endpoints administrativos sem autenticação)
File:            app.py:47-78
Description:     /admin/reset-db (linhas 47-57) executa DELETE em 4 tabelas
                 diretamente no handler da rota, sem nenhuma verificação de
                 autenticação/autorização. /admin/query (linhas 59-78) recebe uma
                 string SQL arbitrária do corpo da requisição (dados.get("sql")) e
                 executa via cursor.execute(query) sem nenhuma restrição — é, na
                 prática, um endpoint de execução de SQL arbitrário exposto
                 publicamente.
Impact:          Qualquer cliente não autenticado pode apagar todo o banco de dados
                 de produção ou executar comandos SQL arbitrários (incluindo DROP
                 TABLE, UPDATE em massa, ou leitura de qualquer tabela).
Recommendation:  Remover /admin/query da API pública (não há caso de uso legítimo
                 para executar SQL arbitrário via HTTP). Proteger /admin/reset-db
                 com autenticação/autorização de administrador antes de mover a
                 lógica para Model/Controller.
Category:        Correção obrigatória
Behavior change: Antes — POST /admin/reset-db sem token retorna 200 e apaga o banco.
                 Depois — retorna 401/403 sem autenticação de administrador válida.
                 Antes — POST /admin/query com {"sql": "DROP TABLE produtos"} retorna
                 200 e executa o comando.
                 Depois — endpoint removido (404) ou bloqueado (403) para qualquer
                 SQL vindo do cliente.

[HIGH] Estado Global Mutável / Conexão não thread-safe
File:            database.py:4;10
Description:     db_connection = None (linha 4) é variável global de módulo,
                 atribuída dentro de get_db() com sqlite3.connect(...,
                 check_same_thread=False) (linha 10), compartilhada por todas as
                 requisições concorrentes.
Impact:          Requisições concorrentes compartilham a mesma conexão SQLite sem
                 sincronização, risco de corrupção de estado sob carga.
Recommendation:  Usar conexão por request (ex.: flask.g) ou pool de conexões,
                 eliminando a variável global.
Category:        Refatoração estrutural

[HIGH] Senha armazenada em texto plano e exposta via API
File:            database.py:75-83;models.py:72-87;89-103;105-120;122-131
Description:     Senhas são inseridas em texto plano no seed (database.py:75-83) e
                 em criar_usuario (models.py:122-131), comparadas em texto plano em
                 login_usuario (models.py:109-111), e o campo "senha" é incluído
                 literalmente no dicionário serializado retornado por
                 get_todos_usuarios (models.py:83) e get_usuario_por_id (models.py:99)
                 — ou seja, GET /usuarios e GET /usuarios/<id> vazam a senha de
                 qualquer usuário em texto plano.
Impact:          Um dump do banco ou uma simples chamada GET /usuarios expõe a
                 senha de todos os usuários.
Recommendation:  Hashear senha com werkzeug.security.generate_password_hash /
                 check_password_hash; remover o campo senha de qualquer serialização
                 de resposta.
Category:        Correção obrigatória
Behavior change: Antes — GET /usuarios retorna o campo "senha" em texto plano para
                 cada usuário.
                 Depois — GET /usuarios não inclui o campo "senha" na resposta.
                 Antes — POST /login compara senha em texto plano.
                 Depois — POST /login valida via hash; resposta observável (200/401)
                 permanece a mesma para credenciais corretas/incorretas.

[MEDIUM] Ausência de Separação de Responsabilidade de Config
File:            app.py:8;database.py:5
Description:     app.config["DEBUG"] = True (app.py:8) e db_path = "loja.db"
                 (database.py:5) são configurações hardcoded diretamente nos
                 arquivos de aplicação, sem nenhum módulo central de config.
Impact:          Difícil auditar quais variáveis de ambiente a aplicação precisa;
                 impossível trocar ambiente (dev/prod) sem editar código-fonte.
Recommendation:  Centralizar DEBUG, DB_PATH e SECRET_KEY em um único módulo config.py
                 lido de variáveis de ambiente.
Category:        Refatoração estrutural

[MEDIUM] Ausência de Validação na Fronteira
File:            controllers.py:118-121
Description:     Em buscar_produtos(), preco_min = float(preco_min) e
                 preco_max = float(preco_max) são executados sem verificar se o
                 valor é numérico. Um valor não numérico levanta ValueError, que é
                 capturado apenas pelo except genérico da função e retorna 500.
Impact:          Input inválido do cliente (ex.: preco_min=abc) gera erro 500 em vez
                 de 400, expondo mensagem de exceção interna na resposta.
Recommendation:  Validar explicitamente que preco_min/preco_max são numéricos antes
                 da conversão e retornar 400 com mensagem clara caso não sejam.
Category:        Correção obrigatória
Behavior change: Antes — GET /produtos/busca?preco_min=abc retorna 500
                 {"erro": "could not convert string to float: 'abc'"}.
                 Depois — retorna 400 {"erro": "preco_min inválido"}.

[MEDIUM] Violação de SRP em relatorio_vendas()
File:            models.py:235-273
Description:     Uma única função de 39 linhas executa 5 queries de agregação
                 (acesso a dados), calcula desconto e ticket médio (regra de
                 negócio, linhas 256-263;272) e monta o dicionário de resposta
                 (formatação) — as três responsabilidades misturadas na mesma
                 função.
Impact:          Impossível testar a regra de desconto isoladamente do acesso a
                 dados; mudança na regra de negócio arrisca quebrar a query ou a
                 formatação.
Recommendation:  Separar em: repositório de dados (queries), serviço de domínio
                 (cálculo de desconto/ticket médio) e serializer (montagem do dict).
Category:        Refatoração estrutural

[LOW] Logging via print()
File:            app.py:56;83-86;controllers.py:8;11;57;61;106;161;179;182;208-210;219;248;250
Description:     Mensagens de diagnóstico e de domínio ("ENVIANDO EMAIL...",
                 "NOTIFICAÇÃO: Pedido...") são emitidas via print() espalhado pelos
                 dois arquivos, sem nível de severidade, timestamp ou estrutura.
Impact:          Impossível filtrar por severidade em produção ou integrar com
                 ferramentas de observabilidade; logs se misturam ao stdout sem
                 contexto.
Recommendation:  Substituir por um logger configurado (módulo logging do Python)
                 com níveis (INFO/ERROR) e formatação consistente.
Category:        Refatoração estrutural

[LOW] Magic Numbers na lógica de desconto
File:            models.py:257-263
Description:     Percentuais de desconto (0.1, 0.05, 0.02) e limites de faturamento
                 (10000, 5000, 1000) estão hardcoded diretamente nas condicionais de
                 relatorio_vendas(), sem constante nomeada.
Impact:          Uma mudança nas regras comerciais de desconto exige caçar números
                 soltos no código-fonte.
Recommendation:  Extrair para constantes nomeadas (ex.: DESCONTO_FAIXA_1 = 0.1) em
                 um módulo de domínio ou config.
Category:        Refatoração estrutural

--------------------------------
Deprecated APIs
--------------------------------
Stack verificada: Python + Flask 3.1.1

Nenhuma API deprecated identificada para a stack Flask 3.1.1 — não foram
encontrados usos de @app.before_first_request, from flask.ext. ou
flask.escape()/from flask import escape nos arquivos .py do projeto.

--------------------------------
Total: 11 findings | CRITICAL: 4 | HIGH: 2 | MEDIUM: 3 | LOW: 2
================================
```

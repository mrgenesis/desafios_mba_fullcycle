```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~183 lines of code
Date:    2026-07-25

--------------------------------
Summary
--------------------------------
CRITICAL : 3
HIGH     : 3
MEDIUM   : 3
LOW      : 2
TOTAL    : 11 findings

--------------------------------
Findings
--------------------------------

[CRITICAL] God File / Monolítico
File:            src/AppManager.js:1-142
Description:     Uma única classe concentra inicialização do banco (initDb,
                 linhas 10-23), definição de rotas (setupRoutes, linha 25),
                 lógica de negócio de checkout, processamento de pagamento,
                 criação de usuário e geração de relatório financeiro. Não
                 existem subpastas models/, controllers/ ou routes/.
Impact:          Qualquer mudança de regra de negócio, rota ou schema exige
                 tocar na mesma classe; impossível testar camadas isoladamente;
                 alto risco de regressão a cada alteração.
Recommendation:  Separar em camadas MVC (config/, models/, controllers/,
                 routes/) conforme architecture-guidelines.md.
Category:        Refatoração estrutural

[CRITICAL] Fat Route / Acesso Direto ao Banco na Rota
File:            src/AppManager.js:28-137
Description:     Os três handlers de rota (POST /api/checkout linhas 28-78,
                 GET /api/admin/financial-report linhas 80-129, DELETE
                 /api/users/:id linhas 131-137) executam SQL diretamente
                 (this.db.get/all/run) e contêm toda a regra de negócio
                 (cálculo de pagamento, validação de curso, matrícula) dentro
                 do próprio handler, sem Model nem Controller intermediários.
Impact:          Impossível reutilizar ou testar a lógica isoladamente da
                 camada HTTP; duplicação de acesso a dados entre rotas.
Recommendation:  Extrair Model (queries) e Controller (regra de negócio) para
                 cada domínio, conforme refactoring-playbook.md.
Category:        Refatoração estrutural

[CRITICAL] Segredo / Configuração Hardcoded
File:            src/utils.js:1-7
Description:     dbPass ("senha_super_secreta_prod_123") e paymentGatewayKey
                 ("pk_live_1234567890abcdef" — prefixo "pk_live_" indica chave
                 de produção de um gateway de pagamento real) estão hardcoded
                 no objeto config. paymentGatewayKey é logado em texto plano no
                 console a cada checkout (AppManager.js:45).
Impact:          Segredo de produção versionado no repositório e adicionalmente
                 vazado nos logs da aplicação a cada requisição de checkout.
Recommendation:  Ler todos os campos de config de variáveis de ambiente
                 (process.env), com valores default apenas para desenvolvimento
                 local; remover o log da chave do gateway de pagamento.
Category:        Correção obrigatória
Behavior change: Antes — cada POST /api/checkout imprime a paymentGatewayKey
                 completa no console do servidor.
                 Depois — o console não deve mais expor a chave do gateway de
                 pagamento; o corpo das respostas HTTP não muda.

[HIGH] Callback Hell / Pyramid of Doom
File:            src/AppManager.js:37-77
Description:     O fluxo de checkout aninha callbacks em 5 níveis de
                 profundidade (db.get → db.get → db.run → db.run → db.run).
                 Erros em callbacks internos retornam apenas mensagens genéricas
                 ("Erro DB", "Erro Matrícula", "Erro Pagamento") sem contexto.
Impact:          Fluxo de negócio difícil de ler, testar e manter; tratamento
                 de erro inconsistente entre os níveis de callback.
Recommendation:  Converter para async/await usando a API de Promises do
                 sqlite3 (ou wrapper promisificado), achatando o fluxo em
                 sequência linear.
Category:        Refatoração estrutural

[HIGH] Hashing de senha inseguro
File:            src/utils.js:17-23;AppManager.js:68
Description:     badCrypto() não é uma função de hash criptográfico: repete a
                 codificação Base64 da senha 10000 vezes e trunca o resultado
                 para 10 caracteres (linhas 18-22). É determinística, sem sal,
                 e usada para "hashear" a senha de novos usuários no checkout
                 (AppManager.js:68).
Impact:          A "senha hasheada" é trivialmente reversível/colidível; não
                 oferece nenhuma proteção real em caso de vazamento do banco.
Recommendation:  Substituir por bcrypt (ou equivalente) com sal por usuário.
Category:        Correção obrigatória
Behavior change: Antes — a senha é transformada por badCrypto() (determinística,
                 sem sal) antes de ser armazenada.
                 Depois — a senha deve ser armazenada com bcrypt (não
                 determinística); o corpo das respostas HTTP do checkout não
                 muda (a senha nunca é retornada ao cliente).

[HIGH] Estado Global Mutável
File:            src/utils.js:9-10
Description:     globalCache = {} (linha 9) é objeto de módulo mutado por
                 logAndCache() a cada checkout (utils.js:14). totalRevenue = 0
                 (linha 10) é exportado mas nunca incrementado em nenhum lugar
                 do código — estado morto, porém declarado como mutável global.
Impact:          globalCache é compartilhado por todas as requisições
                 concorrentes sem nenhuma sincronização; risco de
                 inconsistência sob carga.
Recommendation:  Eliminar variáveis de módulo mutável; usar cache externo
                 (Redis) se necessário, ou removê-las se não usadas
                 (totalRevenue).
Category:        Refatoração estrutural

[MEDIUM] Ausência de Validação na Fronteira / senha padrão fraca
File:            src/AppManager.js:29-35;68
Description:     O campo pwd (senha) não é obrigatório na validação de entrada
                 (linha 35 só exige usr, eml, c_id, card) — se ausente, o
                 código usa o literal "123456" como senha padrão para o novo
                 usuário (linha 68). Não há validação de formato de e-mail nem
                 do número de cartão além de um startsWith("4").
Impact:          Contas podem ser criadas com uma senha previsível e conhecida
                 publicamente (esta auditoria), permitindo login não autorizado
                 posterior.
Recommendation:  Tornar pwd obrigatório; rejeitar checkout sem senha com 400 em
                 vez de aplicar um default fraco.
Category:        Correção obrigatória
Behavior change: Antes — POST /api/checkout sem o campo "pwd" retorna 200 e cria
                 o usuário com a senha "123456".
                 Depois — mesma requisição deve retornar 400 com corpo indicando
                 que a senha é obrigatória.

[MEDIUM] Exclusão de usuário deixa dados órfãos
File:            src/AppManager.js:131-137
Description:     DELETE /api/users/:id apaga a linha em users sem tratar
                 enrollments nem payments relacionados — o próprio código
                 documenta isso na mensagem de resposta ("mas as matrículas e
                 pagamentos ficaram sujos no banco", linha 135).
Impact:          Registros de enrollments/payments passam a referenciar um
                 usuário inexistente, corrompendo a integridade referencial e
                 distorcendo o relatório financeiro.
Recommendation:  Ao excluir um usuário, excluir (ou anonimizar) em cascata
                 enrollments e payments relacionados na mesma transação.
Category:        Correção obrigatória
Behavior change: Antes — DELETE /api/users/1 retorna 200 e deixa enrollments/
                 payments órfãos referenciando o usuário excluído.
                 Depois — DELETE /api/users/1 também remove (ou anonimiza) os
                 enrollments e payments associados; resposta de sucesso
                 permanece 200.

[MEDIUM] Queries N+1 no relatório financeiro
File:            src/AppManager.js:80-129
Description:     Para cada curso (linha 89), busca-se enrollments (linha 92);
                 para cada enrollment, busca-se usuário (linha 104) e pagamento
                 (linha 106) em queries separadas dentro de loops aninhados. Com
                 N cursos e M matrículas por curso, gera 1 + N + N×M×2 queries.
Impact:          Performance degrada linearmente/quadraticamente com o volume de
                 dados; em produção pode gerar centenas de queries por request.
Recommendation:  Substituir por uma única query com JOIN entre courses,
                 enrollments, users e payments.
Category:        Refatoração estrutural

[LOW] Nomes de variáveis sem semântica
File:            src/AppManager.js:29-33
Description:     Parâmetros do checkout: u (nome), e (email), p (senha), cid
                 (course_id), cc (cartão). Impossível entender a intenção sem
                 ler o corpo completo da função.
Impact:          Legibilidade prejudicada; onboarding mais lento; risco de troca
                 acidental de parâmetros.
Recommendation:  Renomear para nome, email, senha, cursoId, cartao (ou
                 equivalentes em inglês consistentes com o resto do código).
Category:        Refatoração estrutural

[LOW] Simulação de pagamento sem flag explícita
File:            src/AppManager.js:46
Description:     let status = cc.startsWith("4") ? "PAID" : "DENIED" valida
                 cartão como aprovado apenas pelo primeiro dígito (bandeira
                 Visa), sem nenhum comentário ou flag indicando que é uma
                 simulação e não uma integração real de gateway de pagamento.
Impact:          Pode enganar um mantenedor futuro a acreditar que existe
                 processamento de pagamento real; risco de ir para produção sem
                 gateway de fato integrado.
Recommendation:  Isolar em um módulo de "payment gateway" explicitamente
                 marcado como simulação/mock, documentando a necessidade de
                 substituição antes de produção.
Category:        Refatoração estrutural

--------------------------------
Deprecated APIs
--------------------------------
Stack verificada: Node.js + Express 4.18.2

Nenhuma API deprecated identificada para a stack Express 4.18.2 — não foram
encontrados usos de app.del(, require('url').parse( nos arquivos .js do
projeto, e o pacote "body-parser" não aparece como dependência separada
(o projeto já usa express.json() nativo).

--------------------------------
Total: 11 findings | CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2
================================
```

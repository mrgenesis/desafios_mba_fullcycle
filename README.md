# Skill de Auditoria e Refatoração Arquitetural

Implementação da skill `refactor-arch` para o Claude Code que analisa, audita e refatora projetos legados para o padrão MVC, de forma agnóstica de tecnologia.

---

## Análise Manual

### Projeto 1 — code-smells-project

| Severidade | Anti-pattern                                    | Arquivo:Linha                                                                            | Impacto                                                                                                                                                                                                                    |
| ---------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CRITICAL   | SQL Injection                                   | `models.py:28, 48–49, 58–61, 68, 92, 109–111, 127–129, 149, 158, 163, 174, 279, 291–296` | Queries montadas por concatenação de string permitem injeção de SQL arbitrário. Ex: `"SELECT * FROM produtos WHERE id = " + str(id)` aceita `1 OR 1=1` sem nenhuma sanitização.                                            |
| HIGH       | Senhas armazenadas em texto plano               | `models.py:83, 99, 127–129` e `database.py:78`                                           | Senhas são inseridas e consultadas sem hash. Um dump do banco expõe todas as credenciais dos usuários.                                                                                                                     |
| MEDIUM     | Estado global mutável / conexão não thread-safe | `database.py:4, 9–10`                                                                    | `db_connection = None` como variável global com `check_same_thread=False`, múltiplas requisições concorrentes compartilham a mesma conexão SQLite sem sincronização.                                                       |
| MEDIUM     | Endpoint destrutivo sem autenticação            | `app.py:47–57`                                                                           | `/admin/reset-db` apaga todas as linhas das 4 tabelas sem exigir autenticação. Qualquer cliente pode esvaziar o banco em produção.                                                                                         |
| LOW        | Logging via `print()`                           | `controllers.py:8, 11, 57, 61, 106, 161, 179, 208–210`                                   | Mensagens de diagnóstico com `print()` dispersas no código, sem nível de severidade, sem timestamp, sem estrutura. Impossível filtrar em produção ou integrar com ferramentas de observabilidade.                          |
| LOW        | Magic numbers na lógica de desconto             | `models.py:257–263`                                                                      | Percentuais de desconto (`0.1`, `0.05`, `0.02`) e limites de faturamento (`10000`, `5000`, `1000`) hardcoded na função `relatorio_vendas()`. Uma mudança nas regras de negócio exige caçar números espalhados pelo código. |

**Total: 1 CRITICAL | 1 HIGH | 2 MEDIUM | 2 LOW = 6 findings**

---

### Projeto 2 — ecommerce-api-legacy

| Severidade | Anti-pattern                                    | Arquivo:Linha              | Impacto                                                                                                                                                                                                                   |
| ---------- | ----------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CRITICAL   | God Class                                       | `src/AppManager.js:1–141`  | Uma única classe concentra: inicialização do banco, definição de rotas, lógica de checkout, processamento de pagamento, criação de usuário e geração de relatório financeiro. Qualquer mudança tem risco de quebrar tudo. |
| HIGH       | Callback Hell / Pyramid of Doom                 | `src/AppManager.js:36–77`  | O fluxo de checkout aninha callbacks 5 níveis de profundidade: `db.get → db.get → db.run → db.run → db.run`. Erros em callbacks internos são silenciados ou retornam apenas `"Erro DB"` sem contexto.                     |
| MEDIUM     | Estado global mutável                           | `src/utils.js:9–10`        | `globalCache` e `totalRevenue` são variáveis de módulo compartilhadas por todas as requisições. Requisições concorrentes podem corromper o estado.                                                                        |
| MEDIUM     | N+1 Query Problem no relatório financeiro       | `src/AppManager.js:80–129` | Para cada curso: busca enrollments; para cada enrollment: busca usuário + busca pagamento em callbacks separados. Com N cursos e M alunos por curso, gera `1 + N + N×M×2` queries.                                        |
| LOW        | Nomes de variáveis sem semântica                | `src/AppManager.js:29–33`  | Parâmetros do checkout: `u` (nome), `e` (email), `p` (senha), `cid` (course_id), `cc` (cartão). Impossível entender a intenção sem ler o contexto completo.                                                               |
| LOW        | Lógica de pagamento simulada sem flag explícita | `src/AppManager.js:46`     | `let status = cc.startsWith("4") ? "PAID" : "DENIED"`, valida cartão Visa pelo primeiro dígito sem nenhum comentário indicando que é simulação, o que pode enganar mantenedores.                                          |

**Total: 1 CRITICAL | 1 HIGH | 2 MEDIUM | 2 LOW = 6 findings**

---

### Projeto 3 — task-manager-api

| Severidade | Anti-pattern                                          | Arquivo:Linha                                                                                                   | Impacto                                                                                                                                                                                                                                           |
| ---------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CRITICAL   | Credenciais hardcoded                                 | `app.py:13` e `services/notification_service.py:9–10`                                                           | `SECRET_KEY = 'super-secret-key-123'` no app; email `taskmanager@gmail.com` e `email_password = 'senha123'` hardcoded no `NotificationService`.                                                                                                   |
| HIGH       | Lógica de negócio nas Routes; ausência de Controllers | `routes/task_routes.py:11–299` e `routes/user_routes.py:10–212`                                                 | As rotas executam queries de banco diretamente (`Task.query.filter_by(...)`), validam regras de negócio e serializam respostas — tudo no mesmo lugar. Sem Controller intermediário, não é possível reutilizar a lógica nem testá-la isoladamente. |
| MEDIUM     | Código duplicado; lógica `overdue` em 5 lugares       | `routes/task_routes.py:30–39, 71–80, 281–288`, `routes/user_routes.py:171–180`, `routes/report_routes.py:33–43` | O bloco de verificação de atraso (`if t.due_date < datetime.utcnow() and status not in [...]`) é copiado em 5 funções diferentes. Uma mudança na regra exige edição em 5 pontos.                                                                  |
| MEDIUM     | Token JWT falso sem autenticação real                 | `routes/user_routes.py:210`                                                                                     | `'token': 'fake-jwt-token-' + str(user.id)` — o login retorna um token previsível e não validável. Não há middleware de autenticação protegendo nenhuma rota.                                                                                     |
| LOW        | Service instanciado mas nunca utilizado               | `services/notification_service.py:1–48`                                                                         | `NotificationService` implementa envio de e-mail e notificações mas não é importado nem chamado por nenhuma rota. Código morto sem clareza se foi removido intencionalmente.                                                                      |
| LOW        | Imports não utilizados                                | `routes/task_routes.py:7` e `app.py:7`                                                                          | `import json, os, sys, time` em `task_routes.py` — nenhum desses módulos é usado. `import os, sys, json` em `app.py` — apenas `datetime` é efetivamente utilizado.                                                                                |

**Total: 1 CRITICAL | 1 HIGH | 2 MEDIUM | 2 LOW = 6 findings**

---

## Construção da Skill

### Decisões de design

A skill é composta por um arquivo principal de orquestração (`SKILL.md`) e cinco arquivos de referência especializados. Essa separação foi deliberada: o `SKILL.md` funciona como um **prompt de agente** — instrui o Claude sobre o que fazer e em que ordem —, enquanto os arquivos de referência fornecem o **conhecimento de domínio** que o agente consulta durante a execução. Nenhum arquivo de referência contém instruções de fluxo; nenhuma instrução de fluxo contém conhecimento de detecção.

**Fluxo sequencial em 3 fases com pausa obrigatória**

A Fase 2 termina com uma pergunta explícita ao usuário antes de qualquer modificação de arquivo. Isso é declarado no `SKILL.md` como obrigação — não como comportamento esperado — porque o agente tende a antecipar a próxima ação sem aguardar confirmação. A pausa é o ponto de controle humano que separa auditoria de execução.

**Duas categorias de correção para a Fase 3**

Durante a construção surgiu a necessidade de distinguir dois tipos de mudança ao refatorar:

- **Refatoração estrutural** — reorganiza o código sem alterar o contrato da API (rotas, payloads, status codes permanecem idênticos). Ex.: extrair um God File em camadas MVC.
- **Correção obrigatória** — altera intencionalmente o comportamento para torná-lo correto. Ex.: SQL Injection corrigido começa a rejeitar inputs maliciosos; credencial hardcoded é removida e passa a exigir variável de ambiente.

Essa distinção impacta diretamente a validação: para refatoração estrutural, qualquer divergência do baseline reprova; para correção obrigatória, a resposta **deve** diferir do baseline — e o sistema reprova se ainda se comportar como antes. O campo `Behavior change` no template de relatório documenta o par antes/depois e é a fonte de verdade usada na comparação da Fase 3.

**Seed com IDs fixos e Matriz de Validação**

A Fase 3 exige que a aplicação original seja iniciada e os endpoints exercitados **antes** de qualquer alteração de código. O seed usa IDs explícitos e fixos (`INSERT INTO produtos (id, nome) VALUES (1, 'Produto Seed A')`), nunca deixando o banco gerar IDs por auto-increment. Isso garante que as fixtures referenciem entidades conhecidas (`GET /produtos/1`) e que as respostas capturadas sejam determinísticas — não dependentes do estado anterior do banco.

Após capturar o baseline, e ainda antes de tocar em qualquer arquivo, a Fase 3 gera uma **Matriz de Validação**: uma tabela com uma linha por fixture que declara antecipadamente o critério de aprovação de cada endpoint:

| Fixture | IDs do seed | Baseline capturado | Esperado pós-refatoração | Fonte |
|---|---|---|---|---|
| `GET /produtos/1` | produto.id=1 | `200 {"id":1,...}` | idêntico ao baseline | Refatoração estrutural |
| `POST /usuarios` (sem "email") | — | `200` (sem validação) | `400 {"error":"email obrigatório"}` | Correção obrigatória — Finding #N |

- Endpoints não mencionados em nenhum `Behavior change` → "idêntico ao baseline"
- Endpoints mencionados em um `Behavior change` → comportamento "Depois" daquele finding

A matriz é salva em `reports/validation-matrix-<projeto>.md` antes de qualquer refatoração e é a única fonte de verdade consultada na comparação final — eliminando julgamento do agente no momento da validação.

**Cinco arquivos de referência e seus papéis**

| Arquivo | Papel | Agnóstico? |
|---|---|---|
| `project-analysis.md` | Heurísticas de detecção de stack, banco e arquitetura | Não — intencionalmente específico por linguagem |
| `anti-patterns-catalog.md` | 14 anti-patterns com sinais de detecção, severidade e categoria | Sinais específicos; estrutura agnóstica |
| `report-template.md` | Formato padronizado do relatório da Fase 2 | Sim |
| `architecture-guidelines.md` | Regras de responsabilidade por camada MVC | Sim |
| `refactoring-playbook.md` | 13 padrões de transformação com exemplos pseudocódigo | Sim |

---

### Anti-patterns incluídos no catálogo e justificativa

O catálogo tem 14 anti-patterns distribuídos entre as severidades do desafio. Os de severidade CRITICAL e HIGH cobrem falhas que comprometem segurança, testabilidade e manutenção estrutural. Os de MEDIUM e LOW cobrem problemas de performance e legibilidade recorrentes nos três projetos analisados.

| # | Anti-pattern | Severidade | Categoria | Justificativa de inclusão |
|---|---|---|---|---|
| 1 | God File / Monolítico | CRITICAL | Refatoração estrutural | Presente no projeto 1 (`models.py`) e projeto 2 (`AppManager.js`); é a violação mais grave de MVC |
| 2 | Fat Route | CRITICAL | Refatoração estrutural | Lógica de negócio nas rotas é o anti-pattern mais comum em APIs Flask/Express sem Controller |
| 3 | Acesso Direto ao Banco na Rota | CRITICAL | Refatoração estrutural | Corolário do Fat Route — queries dentro de handlers impedem trocar o banco sem editar rotas |
| 4 | Segredo / Configuração Hardcoded | CRITICAL | Correção obrigatória | Presente nos projetos 1 e 3; credencial no código é risco de segurança imediato |
| 5 | SQL Injection | CRITICAL | Correção obrigatória | Presente no projeto 1 com concatenação direta de `str(id)` em queries; vulnerabilidade crítica de segurança |
| 6 | Tratamento de Erros Duplicado | HIGH | Correção obrigatória | Blocos try/catch genéricos repetidos por rota geram comportamento inconsistente entre endpoints |
| 7 | Ausência de Validação na Fronteira | MEDIUM | Correção obrigatória | `request.json['campo']` sem verificação de presença retorna 500 onde deveria retornar 400 |
| 8 | Estado Global Mutável | HIGH | Refatoração estrutural | Presente nos projetos 1 (`db_connection` global) e 2 (`globalCache`, `totalRevenue`) |
| 9 | Acoplamento Forte / Ausência de DI | HIGH | Refatoração estrutural | Controllers que instanciam dependências internas não são testáveis isoladamente |
| 10 | Violação de SRP | MEDIUM | Refatoração estrutural | Função que faz query + regra de negócio + serialização — cada responsabilidade precisa ir para sua camada |
| 11 | Import Circular | MEDIUM | Refatoração estrutural | Ciclos de importação causam erros de inicialização difíceis de rastrear em projetos em crescimento |
| 12 | Queries N+1 | MEDIUM | Refatoração estrutural | Presente no projeto 2 (`AppManager.js:80–129`); degrada performance linearmente com volume de dados |
| 13 | Magic Numbers / Strings sem Nome | LOW | Refatoração estrutural | Presente no projeto 1 (`models.py:257–263`) com percentuais de desconto hardcoded |
| 14 | Ausência de Separação de Config | MEDIUM | Refatoração estrutural | `os.environ.get()` ou `process.env` chamados em múltiplos arquivos em vez de um módulo de config único |

Além dos 14 anti-patterns, o catálogo inclui uma seção de **APIs deprecated por stack** (Flask, Django, Express/Node.js) com sinais de detecção específicos. Findings de API deprecated recebem severidade HIGH e categoria "Refatoração estrutural" — substituir uma API deprecated troca a sintaxe sem alterar o contrato observável da API.

---

### Como a skill é agnóstica de tecnologia

A skill opera em dois registros distintos: **detecção** (específica por linguagem, necessariamente) e **orquestração** (agnóstica, obrigatoriamente).

**Detecção intencionalmente específica**

`project-analysis.md` e os sinais de detecção em `anti-patterns-catalog.md` são específicos por linguagem — e isso é correto. "Sinal de detecção" precisa ser acionável: `from flask import` é um sinal concreto; "importa o framework web" não é. Durante a construção, o `project-analysis.md` foi refinado para deixar explícito que `from flask import` deve ser procurado nos **arquivos `.py` do projeto**, não no `requirements.txt` (que é um manifesto de dependências, não código). Isso eliminou uma fonte de falso positivo: `flask` pode aparecer em `requirements.txt` de um projeto Django como sub-dependência.

A detecção de framework usa **dois sinais independentes** por framework — arquivo de dependências e arquivo de código-fonte. Basta um deles para confirmar o framework.

**Orquestração agnóstica**

O `SKILL.md` não menciona nenhuma linguagem, extensão de arquivo ou comando de boot específico. As referências são sempre relativas à stack detectada na Fase 1:

- Em vez de `node_modules/`, `venv/`, `__pycache__/` → "pastas de dependências e cache da stack"
- Em vez de `python app.py` ou `npm start` → "comando idiomático da stack detectada na Fase 1"
- Em vez de `.py`, `.js` → a Fase 1 detecta a extensão; as fases seguintes herdam esse contexto

O `architecture-guidelines.md` descreve as camadas MVC em termos puramente abstratos: responsabilidades, o que pertence e o que nunca pertence em cada camada, sem qualquer exemplo de código.

O `refactoring-playbook.md` usa o identificador ` ```pseudocode ` em todos os blocos de código, sinalizando explicitamente que os exemplos são pseudocódigo agnóstico — não código executável em nenhuma linguagem específica. O agente aplica os idiomas da linguagem detectada na Fase 1 ao traduzir cada padrão.

---

### Desafios encontrados nas iterações

**1. Clareza na detecção de framework**

O `project-analysis.md` inicial listava sinais como `from flask import` sem especificar onde buscá-los. O `requirements.txt` contém `flask` como string, mas isso é o nome do pacote, não um import. A correção foi reestruturar a tabela de detecção com uma coluna "Onde buscar" explícita para cada sinal, tornando claro que imports só são válidos em arquivos de código-fonte.

**2. Equilíbrio entre agnóstico e específico**

A versão inicial de `architecture-guidelines.md` incluía exemplos separados por linguagem (Flask Blueprint, Express Router). A pergunta "por que o arquivo não ter apenas um modelo abstrato para todas as linguagens?" levou a uma reescrita completa do arquivo em formato puramente abstrato. A conclusão foi estabelecer uma distinção explícita: arquivos de **orquestração** (`SKILL.md`, `architecture-guidelines.md`, `refactoring-playbook.md`) devem ser agnósticos; arquivos de **detecção** (`project-analysis.md`, `anti-patterns-catalog.md`) são intencionalmente específicos por linguagem, porque sinais de detecção sem linguagem não são acionáveis.

**3. Middlewares não faz parte do MVC**

Questionado se Middlewares era um componente do MVC, o `architecture-guidelines.md` foi atualizado para deixar explícito: Middlewares é uma camada de **suporte** ao pipeline HTTP — não faz parte do MVC clássico. O MVC foi criado antes de frameworks web; a camada de middleware existe porque frameworks web operam sobre um ciclo HTTP que exige pontos de intercepção transversais. Tratá-la como uma camada separada evita que se misture ao Controller (violação de SRP) ou ao entry point (God File).

**4. Referência circular entre SKILL.md e o catálogo**

O `SKILL.md` na Fase 3 referenciava as categorias "Refatoração estrutural" e "Correção obrigatória" como se já existissem no catálogo — mas o catálogo não tinha esse campo. Isso criava uma referência a uma fonte de verdade inexistente. A correção foi adicionar o campo `**Categoria:**` a todos os 14 anti-patterns do catálogo, tornando o catálogo a fonte autoritativa dessas classificações e o SKILL.md apenas um consumidor delas.

**5. Cobertura incompleta do playbook**

Os anti-patterns #10 (Violação de SRP) e #11 (Import Circular) não tinham padrão correspondente no playbook. O catálogo tinha os sinais de detecção e a Fase 2 encontraria esses problemas — mas a Fase 3 não teria instrução de como corrigi-los. Foram adicionados os padrões "Separação de Responsabilidades" e "Quebra de Ciclo de Importação" ao playbook.

**6. Notação de código nos exemplos do playbook**

Os blocos de código dos padrões usavam identificadores de linguagem específicos (`python`, `javascript`). Isso sinalizava ao agente que os exemplos eram código executável — não pseudocódigo — e criava ambiguidade sobre qual linguagem usar em projetos com stack diferente. A adoção do identificador `pseudocode` resolveu isso: é a notação reconhecidamente usada para indicar código falso/ilustrativo, deixando inequívoco que o agente deve adaptar para a linguagem detectada na Fase 1.

---

## Resultados

> _Preencher após executar a skill nos 3 projetos._

### Artefatos gerados por projeto

A Fase 3 gera dois arquivos em `reports/` além do relatório de auditoria da Fase 2:

| Arquivo | Fase | Conteúdo |
|---|---|---|
| `reports/audit-<projeto>.md` | 2 | Relatório de auditoria com todos os findings |
| `reports/validation-matrix-<projeto>.md` | 3 | Matriz com critério de aprovação por fixture, gerada antes da refatoração |

### Resumo dos relatórios de auditoria

| Projeto              | CRITICAL | HIGH | MEDIUM | LOW | Total |
| -------------------- | -------- | ---- | ------ | --- | ----- |
| code-smells-project  | —        | —    | —      | —   | —     |
| ecommerce-api-legacy | —        | —    | —      | —   | —     |
| task-manager-api     | —        | —    | —      | —   | —     |

### Estrutura antes/depois

<!-- Mostrar árvore de diretórios antes e depois da refatoração para cada projeto. -->

### Checklist de validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [ ] Linguagem detectada corretamente (Python)
- [ ] Framework detectado corretamente (Flask)
- [ ] Domínio da aplicação descrito corretamente (E-commerce API)
- [ ] Número de arquivos analisados condiz com a realidade (4 arquivos)

**Fase 2 — Auditoria**
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (Flask)
- [ ] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [ ] Seed com IDs fixos gerado e aplicado (TRUNCATE + INSERT explícito)
- [ ] Matriz de Validação gerada antes da refatoração (`reports/validation-matrix-code-smells-project.md`)
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints validados linha a linha contra a Matriz de Validação

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [ ] Linguagem detectada corretamente (Node.js)
- [ ] Framework detectado corretamente (Express)
- [ ] Domínio da aplicação descrito corretamente (LMS API)
- [ ] Número de arquivos analisados condiz com a realidade (3 arquivos)

**Fase 2 — Auditoria**
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (Express/Node.js)
- [ ] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [ ] Seed com IDs fixos gerado e aplicado (TRUNCATE + INSERT explícito)
- [ ] Matriz de Validação gerada antes da refatoração (`reports/validation-matrix-ecommerce-api-legacy.md`)
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints validados linha a linha contra a Matriz de Validação

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [ ] Linguagem detectada corretamente (Python)
- [ ] Framework detectado corretamente (Flask)
- [ ] Domínio da aplicação descrito corretamente (Task Manager)
- [ ] Número de arquivos analisados condiz com a realidade

**Fase 2 — Auditoria**
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (`Query.get()` do SQLAlchemy)
- [ ] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [ ] Seed com IDs fixos gerado e aplicado (TRUNCATE + INSERT explícito)
- [ ] Matriz de Validação gerada antes da refatoração (`reports/validation-matrix-task-manager-api.md`)
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models mantidos e melhorados
- [ ] Routes refatoradas para delegar ao Controller
- [ ] Controllers criados para orquestrar fluxo
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints validados linha a linha contra a Matriz de Validação

### Logs / screenshots

<!-- Colar saída do servidor subindo e de curl nos endpoints após cada refatoração. -->

---

## Como Executar

### Pré-requisitos

- Python 3.10+ com `pip`
- Node.js 18+ com `npm`
- Claude Code instalado e autenticado (`claude --version`)

### Instalação das dependências

```bash
# Projeto 1 (Python/Flask)
cd code-smells-project
python -m venv venv
source venv/bin/activate
# No Windows: venv\Scripts\activate
pip install -r requirements.txt

# Projeto 2 (Node.js/Express)
cd ../ecommerce-api-legacy
npm install

# Projeto 3 (Python/Flask)
cd ../task-manager-api
python -m venv venv
source venv/bin/activate
# No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Executar a skill

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

### Validar que a refatoração funcionou

```bash
# Projeto 1
python app.py &
curl http://localhost:5000/health
curl http://localhost:5000/produtos

# Projeto 2
node src/app.js &
curl http://localhost:3000/api/admin/financial-report

# Projeto 3
python app.py &
curl http://localhost:5000/health
curl http://localhost:5000/tasks
```

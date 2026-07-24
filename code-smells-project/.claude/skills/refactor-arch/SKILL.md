---
name: refactor-arch
description: Audita uma codebase (qualquer linguagem/framework) em busca de anti-patterns de arquitetura MVC/SOLID, gera relatório de findings por severidade e refatora o projeto para MVC após confirmação humana. Use quando o usuário pedir para auditar, revisar arquitetura ou refatorar um projeto para o padrão MVC.
---

Você é um especialista em arquitetura de software (padrão MVC e princípios SOLID). Ao ser invocado, execute as 3 fases abaixo, nesta ordem exata, sem pular etapas: **Fase 1 (Análise)** → **Fase 2 (Auditoria, com pausa obrigatória para confirmação humana)** → **Fase 3 (Refatoração, com validação final)**. Cada fase só começa depois que a anterior tiver atingido o critério de saída definido nela.

## Fase 1 — Análise

Objetivo: entender a stack e a arquitetura atual do projeto antes de julgar qualquer problema.

1. Liste os arquivos a partir da raiz do projeto atual. Por enquanto, ignore os detalhes de pastas de dependências e cache da stack (ex.: `.git/`, pastas de pacotes, pastas de cache e bytecode), arquivos de lock e binários/artefatos de build.
2. Detecte linguagem e framework usando as heurísticas de [project-analysis.md](project-analysis.md) (manifestos de dependência, imports no entry point, etc.). Não assuma a stack pelo nome da pasta.
3. Detecte o banco de dados e liste as tabelas/entidades encontradas (schema, `CREATE TABLE`, models de ORM, migrations).
4. Infira o domínio da aplicação a partir de nomes de rotas, tabelas e entidades (ex.: `produtos/pedidos` → e-commerce; `courses/enrollments/payments` → LMS).
5. Avalie o grau de organização **já existente** — não presuma que o projeto está em um único arquivo. Verifique se já há separação em pastas (`models/`, `routes/`, `services/`, etc.) e classifique a arquitetura atual como: monolítica (tudo em poucos arquivos), parcialmente organizada (alguma separação, mas com violações), ou já próxima de MVC.
6. Conte quantos arquivos de código-fonte foram efetivamente analisados (exclua da contagem os ignorados no passo 1).

Critério de saída da Fase 1: você imprimiu o bloco de resumo abaixo, com todos os campos preenchidos com valores reais do projeto (nunca "N/A" ou placeholder) — só então a Fase 2 pode começar.

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework + versão, se identificável>
Dependencies:  <dependências relevantes para a arquitetura>
Domain:        <domínio de negócio inferido>
Architecture:  <classificação da arquitetura atual + breve justificativa>
Source files:  <N> files analyzed
DB tables:     <tabelas/entidades encontradas>
================================
```

## Fase 2 — Auditoria

Objetivo: cruzar o código real do projeto contra o catálogo de anti-patterns e produzir um relatório que o usuário possa revisar antes de qualquer alteração.

1. Percorra os arquivos analisados na Fase 1 e confronte cada trecho relevante com os anti-patterns descritos em [anti-patterns-catalog.md](anti-patterns-catalog.md). Para cada anti-pattern do catálogo, verifique se o sinal de detecção descrito ocorre no código — não invente achados que não tenham um sinal correspondente, e não pule anti-patterns do catálogo sem checar.
2. Para cada problema encontrado, registre: arquivo e linha(s) exatas (nunca aproximadas), descrição do problema, impacto concreto, recomendação de correção, e a severidade conforme a classificação do catálogo (CRITICAL / HIGH / MEDIUM / LOW).
3. Inclua explicitamente a verificação de **APIs deprecated** da stack detectada (ver seção correspondente em [anti-patterns-catalog.md](anti-patterns-catalog.md)), mesmo que o resultado seja "nenhuma encontrada".
4. Monte o relatório seguindo exatamente o formato de [report-template.md](report-template.md), com os findings **ordenados por severidade** (CRITICAL → HIGH → MEDIUM → LOW) e um total geral ao final.
5. Salve o relatório em `reports/audit-<nome-do-projeto>.md` (crie a pasta `reports/` se não existir) e também exiba o relatório completo no terminal.

Critério de saída da Fase 2: o relatório foi salvo e exibido, com no mínimo 5 findings, incluindo pelo menos 1 CRITICAL ou HIGH. Só então pare e peça confirmação.

**Pausa obrigatória — não é opcional e não deve ser implícita.** Depois de exibir o relatório completo, pergunte exatamente:

"Relatório completo. Deseja prosseguir com a refatoração? [y/n]"

Aguarde a resposta do usuário. **Não modifique, crie ou apague nenhum arquivo do projeto antes de receber essa resposta.** Se a resposta for diferente de "y" (ou equivalente afirmativo claro), pare a execução da skill e não inicie a Fase 3.

## Fase 3 — Refatoração

Objetivo: reestruturar o projeto para o padrão MVC, eliminando os problemas do relatório, sem quebrar o comportamento existente.

1. Antes de tocar em qualquer arquivo, garanta que o estado atual é recuperável: se o projeto estiver em um repositório git com mudanças não commitadas relevantes, avise o usuário; caso contrário, prossiga.
2. **Capture o baseline antes de qualquer alteração de código.** Com a aplicação ainda no estado ORIGINAL:
   - Gere um script/rotina de seed com dados determinísticos que cubram os endpoints mapeados na Fase 1. O seed deve:
     - Executar TRUNCATE (ou DELETE sem WHERE) em todas as tabelas relevantes antes de inserir.
     - Inserir registros com **IDs explícitos e fixos** (ex.: `INSERT INTO produtos (id, nome, preco) VALUES (1, 'Produto Seed A', 10.00)`), nunca deixando o banco gerar IDs por auto-increment.
   - Gere as fixtures: um conjunto fixo de requisições (método, rota, payload) por endpoint, referenciando os IDs fixos do seed (ex.: `GET /produtos/1`, `DELETE /pedidos/2`). Inclua ao menos uma requisição de caminho feliz e uma de caminho de erro por endpoint relevante.
   - Suba a aplicação original, aplique o seed, execute as fixtures e salve as respostas (status code + corpo) como baseline. Encerre a aplicação.
3. **Gere a Matriz de Validação** antes de modificar qualquer arquivo. A matriz é a fonte de verdade da comparação final — uma linha por fixture:

   ```
   Fixture (método + rota + payload)   | IDs do seed     | Baseline (capturado)       | Esperado pós-refatoração          | Fonte
   -------------------------------------|-----------------|----------------------------|-----------------------------------|------
   GET /produtos/1                      | produto.id=1    | 200 {"id":1,"nome":"..."}  | idêntico ao baseline              | Refatoração estrutural
   POST /usuarios (sem "email")         | —               | 200 (sem validação)        | 400 {"error":"email obrigatório"} | Correção obrigatória — Finding #N
   ```

   - Para cada fixture cujo endpoint **não** é mencionado em nenhum `Behavior change` de finding `Correção obrigatória`: coluna "Esperado" = "idêntico ao baseline".
   - Para cada fixture cujo endpoint **é** mencionado em um `Behavior change`: coluna "Esperado" = comportamento "Depois" descrito naquele campo.
   - Salve a matriz em `reports/validation-matrix-<nome-do-projeto>.md` e exiba-a no terminal antes de iniciar qualquer alteração de código.
4. Aplique a convenção de estrutura de pastas correspondente à stack detectada na Fase 1, conforme [architecture-guidelines.md](architecture-guidelines.md) (camadas Models, Views/Routes, Controllers, Config e Middlewares).
5. Para cada finding do relatório da Fase 2, aplique a transformação correspondente descrita em [refactoring-playbook.md](refactoring-playbook.md) — não corrija "no geral"; resolva cada anti-pattern com o padrão específico do playbook. Antes de aplicar, consulte [anti-patterns-catalog.md](anti-patterns-catalog.md) e classifique cada correção em uma das duas categorias:
   - **Refatoração estrutural** (anti-patterns cuja correção reorganiza o código sem alterar o contrato da API — ex.: God File, Fat Route, Acoplamento Forte, Queries N+1, Import Circular): rotas, payloads e status codes devem permanecer idênticos ao baseline.
   - **Correção obrigatória de anti-pattern** (anti-patterns cuja correção altera intencionalmente o comportamento para torná-lo correto — ex.: SQL Injection, Ausência de Validação, Segredo Hardcoded, Tratamento de Erros): **a mudança de comportamento é obrigatória** — o sistema deve passar a rejeitar inputs inválidos (400 em vez de 500), negar payloads exploráveis e normalizar respostas de erro.
6. Extraia toda configuração e segredo hardcoded para o módulo de config (variáveis de ambiente com valores default apenas para desenvolvimento local, nunca segredos reais no código).
7. Centralize o tratamento de erros (middleware/error handler único), em vez de tratamento duplicado por rota.
8. Ao final, apresente a nova árvore de diretórios.

**Validação (obrigatória antes de declarar sucesso):**

1. Suba a aplicação refatorada usando o comando idiomático da stack detectada na Fase 1 e confirme que ela inicia sem erros no boot.
2. Aplique o **mesmo seed** (mesmos IDs fixos) e execute as **mesmas fixtures** contra a aplicação refatorada.
3. Compare cada resposta linha a linha com a **Matriz de Validação** gerada no passo 3 — ela é a única fonte de verdade da comparação:
   - **Linha com "idêntico ao baseline":** a resposta deve ser exatamente igual à coluna "Baseline". Qualquer divergência reprova.
   - **Linha com comportamento "Depois" de Correção obrigatória:** a resposta deve corresponder à coluna "Esperado pós-refatoração". A validação aprova se corresponde ao comportamento correto — e **reprova** se ainda corresponder ao comportamento incorreto original (ex.: input inválido ainda retornando 200, SQL ainda executável via injeção).
4. Encerre o processo da aplicação ao final dos testes.
5. **Se o boot falhar ou uma resposta divergir da Matriz de Validação**, não declare sucesso: reporte exatamente qual fixture falhou, o que retornou versus o que a matriz esperava, corrija a causa raiz e repita a comparação. Só reverta a refatoração (voltar ao estado da Fase 2) se, após tentativas de correção, a divergência persistir — e avise o usuário claramente antes de fazê-lo.

Critério de saída da Fase 3: imprima o bloco abaixo com todos os campos preenchidos com valores reais, só então declare a skill concluída.

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Structure:
<raiz>/
├── config/
├── models/
├── controllers/
├── views/ ou routes/
├── middlewares/
└── <entry-point>

Anti-patterns resolved: <N resolvidos>/<N total do relatório>
Remaining:             <N pendentes, ou "none">

Validation
  ✓ Application boots without errors
  ✓ Structural refactoring — all endpoints match baseline
  ✓ Mandatory corrections — all endpoints produce expected behavior
================================
```

Se algum item de validação não puder ser marcado como `✓`, substitua por `✗`, descreva a divergência e explique a causa — não omita nem declare sucesso parcial como total.

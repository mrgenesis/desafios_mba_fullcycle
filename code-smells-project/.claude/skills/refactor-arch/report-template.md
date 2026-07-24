# Template de Relatório de Auditoria

Use este template na Fase 2 para gerar o relatório. Substitua todos os campos entre `<` `>` por valores reais do projeto auditado. A notação `[...]` indica conteúdo opcional e aparece apenas no campo `File` para representar intervalos de linha adicionais não-contíguos (ex.: `models.py:1-40[;120-180]`). Não omita nenhuma seção — preencha com "N/A" apenas quando a seção realmente não se aplicar, com justificativa.

---

## Formato do relatório

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework> <versão>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <YYYY-MM-DD>

--------------------------------
Summary
--------------------------------
CRITICAL : <N>
HIGH     : <N>
MEDIUM   : <N>
LOW      : <N>
TOTAL    : <N> findings

--------------------------------
Findings
--------------------------------

[<CRITICAL|HIGH|MEDIUM|LOW>] <Nome do Anti-Pattern>
File:            <caminho/arquivo.ext>:<linha-início>-<linha-fim>[;<linha-início>-<linha-fim>]
Description:     <Descrição objetiva do problema encontrado no código, citando
                 o trecho exato que gerou o finding.>
Impact:          <Consequência concreta para o sistema — segurança, manutenção,
                 performance ou testabilidade.>
Recommendation:  <Ação específica de correção, referenciando o padrão do
                 refactoring-playbook.md quando aplicável.>
Category:        <Correção obrigatória | Refatoração estrutural>
Behavior change: <Presente apenas quando Category = Correção obrigatória.
                 Descrever o par antes/depois para cada endpoint afetado. Ex.:
                   Antes — POST /usuarios com payload sem 'email' retorna 200
                   Depois — deve retornar 400 com {"error": "email obrigatório"}>

--- (repetir este bloco para cada finding, ordenados por severidade)

--------------------------------
Deprecated APIs
--------------------------------
Stack verificada: <linguagem> + <framework>

<Se encontrado>
[HIGH] API Deprecated: <nome da API>
File:        <caminho/arquivo.ext>:<linha>
Description: <API em uso> está deprecated desde <versão>. Substituir por <alternativa>.
Category:    Refatoração estrutural

<Se não encontrado>
Nenhuma API deprecated identificada para a stack <nome>.

--------------------------------
Total: <N> findings | CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
================================
```

---

## Regras de preenchimento

**Arquivo e linha**
- Sempre informe o caminho relativo à raiz do projeto e as linhas exatas (ex.: `<arquivo>:42-67` ou `<arquivo>:42-67;70-77`).
- Nunca use "aproximadamente" ou intervalos genéricos como `1-350` sem ter verificado as linhas reais.

**Description**
- Cite o trecho concreto que gerou o finding (nome de função, variável ou padrão de código).
- Não repita a definição do anti-pattern — descreva a ocorrência específica no projeto.

**Category**
- `Correção obrigatória` — anti-pattern listado em [anti-patterns-catalog.md](anti-patterns-catalog.md) cuja correção altera o comportamento da API. **Obrigatório preencher o campo `Behavior change`.**
- `Refatoração estrutural` — anti-pattern cuja correção reorganiza o código sem alterar o contrato da API. **Não preencher `Behavior change`** (omitir o campo).

**Behavior change**
- Preencher apenas para findings com `Category: Correção obrigatória`.
- Descrever o par antes/depois para **cada endpoint afetado**, com método HTTP, rota, payload de exemplo, status code atual e status code esperado.
- Este campo é a fonte de verdade usada na validação da Fase 3.

**Ordenação**
- Findings ordenados por severidade: CRITICAL → HIGH → MEDIUM → LOW.
- Dentro de cada severidade, ordenar por impacto (segurança antes de manutenibilidade).

**Deprecated APIs**
- Seção obrigatória mesmo quando vazia — registrar explicitamente "Nenhuma API deprecated identificada".
- Findings de API deprecated recebem severidade HIGH e seguem o mesmo formato dos demais findings.

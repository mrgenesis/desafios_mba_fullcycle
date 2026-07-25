#!/bin/bash
# Fixtures fixas para capturar o baseline (Fase 3) e validar a refatoração
# do ecommerce-api-legacy. O banco é SQLite em memória, recriado do zero a
# cada boot da aplicação com o mesmo seed fixo (initDb): user id=1 "Leonan",
# courses id=1 "Clean Architecture" (997.00) e id=2 "Docker" (497.00),
# enrollment id=1 (user 1, course 1), payment id=1 (997.00, PAID).
set -e
BASE="http://localhost:3000"

req() {
  echo "### $1"
  shift
  curl -s -o /tmp/fixture_body.json -w "HTTP %{http_code}\n" "$@"
  cat /tmp/fixture_body.json
  echo
  echo
}

req "POST /api/checkout (usuario existente, happy path)" -X POST "$BASE/api/checkout" -H "Content-Type: application/json" \
  -d '{"usr":"Leonan","eml":"leonan@fullcycle.com.br","pwd":"123","c_id":1,"card":"4111111111111111"}'

req "POST /api/checkout (novo usuario, sem pwd)" -X POST "$BASE/api/checkout" -H "Content-Type: application/json" \
  -d '{"usr":"Nova Pessoa","eml":"nova@example.com","c_id":2,"card":"4111111111111111"}'

req "POST /api/checkout (cartao recusado)" -X POST "$BASE/api/checkout" -H "Content-Type: application/json" \
  -d '{"usr":"Outra Pessoa","eml":"outra@example.com","pwd":"abc","c_id":1,"card":"5111111111111111"}'

req "POST /api/checkout (curso inexistente)" -X POST "$BASE/api/checkout" -H "Content-Type: application/json" \
  -d '{"usr":"Mais Uma","eml":"maisuma@example.com","pwd":"abc","c_id":999,"card":"4111111111111111"}'

req "POST /api/checkout (campo obrigatorio ausente)" -X POST "$BASE/api/checkout" -H "Content-Type: application/json" \
  -d '{"usr":"Sem Curso","eml":"semcurso@example.com","pwd":"abc","card":"4111111111111111"}'

req "GET /api/admin/financial-report (antes do delete)" "$BASE/api/admin/financial-report"

req "DELETE /api/users/1 (usuario com matriculas/pagamentos)" -X DELETE "$BASE/api/users/1"

req "GET /api/admin/financial-report (depois do delete)" "$BASE/api/admin/financial-report"

req "DELETE /api/users/999 (usuario inexistente)" -X DELETE "$BASE/api/users/999"

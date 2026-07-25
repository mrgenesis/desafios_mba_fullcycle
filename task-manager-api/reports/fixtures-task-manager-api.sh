#!/bin/bash
# Fixtures fixas para capturar o baseline (Fase 3) e validar a refatoração do
# task-manager-api. Rodar sempre logo após `python seed.py` (recria users
# id=1 João/admin, id=2 Maria/user, id=3 Pedro/manager; categories id=1..4;
# tasks id=1..10 com overdue determinístico para id=1 e id=4).
# Campos de data (due_date/created_at/updated_at/generated_at) variam em
# poucos segundos entre a captura do baseline e a validação pós-refatoração
# — não usar como critério de reprovação, apenas os campos derivados
# (ex.: "overdue") e os demais valores.
set -e
BASE="http://localhost:5000"

req() {
  echo "### $1"
  shift
  curl -s -o /tmp/fixture_body.json -w "HTTP %{http_code}\n" "$@"
  cat /tmp/fixture_body.json
  echo
  echo
}

req "GET /users" "$BASE/users"
req "GET /users/1" "$BASE/users/1"
req "POST /login (correto)" -X POST "$BASE/login" -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}'
req "POST /login (senha errada)" -X POST "$BASE/login" -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"errada"}'
req "GET /users/1/tasks" "$BASE/users/1/tasks"
req "GET /tasks" "$BASE/tasks"
req "GET /tasks/1" "$BASE/tasks/1"
req "GET /tasks/search?q=bug" "$BASE/tasks/search?q=bug"
req "GET /tasks/search?priority=abc (invalido)" "$BASE/tasks/search?priority=abc"
req "GET /tasks/stats" "$BASE/tasks/stats"
req "GET /reports/summary" "$BASE/reports/summary"
req "GET /reports/user/1" "$BASE/reports/user/1"
req "GET /categories" "$BASE/categories"
req "PUT /categories/1 (sem corpo JSON)" -X PUT "$BASE/categories/1" -H "Content-Type: application/json" -d 'null'
req "POST /tasks (happy path)" -X POST "$BASE/tasks" -H "Content-Type: application/json" \
  -d '{"title":"Nova Task Fixture","description":"desc","status":"pending","priority":2,"user_id":1,"category_id":1}'
req "PUT /tasks/1 (atualizar status)" -X PUT "$BASE/tasks/1" -H "Content-Type: application/json" \
  -d '{"status":"done"}'
req "DELETE /tasks/2" -X DELETE "$BASE/tasks/2"

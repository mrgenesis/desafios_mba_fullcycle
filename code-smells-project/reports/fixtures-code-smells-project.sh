#!/bin/bash
# Fixtures fixas usadas para capturar o baseline (Fase 3) e validar a
# refatoração do code-smells-project. Rodar sempre após aplicar seed.py
# contra a aplicação (original ou refatorada) já no ar em localhost:5000.
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

req "GET /health" "$BASE/health"
req "GET /produtos" "$BASE/produtos"
req "GET /produtos/1" "$BASE/produtos/1"
req "GET /produtos/999 (not found)" "$BASE/produtos/999"
req "GET /produtos/busca?q=Seed" "$BASE/produtos/busca?q=Seed"
req "GET /produtos/busca?preco_min=abc (invalid numeric)" "$BASE/produtos/busca?preco_min=abc"
req "POST /produtos (happy path)" -X POST "$BASE/produtos" -H "Content-Type: application/json" \
  -d '{"nome":"Produto Fixture","preco":10.5,"estoque":3,"categoria":"informatica"}'
req "POST /produtos (missing preco)" -X POST "$BASE/produtos" -H "Content-Type: application/json" \
  -d '{"nome":"Produto Sem Preco","estoque":3}'
req "PUT /produtos/1 (update)" -X PUT "$BASE/produtos/1" -H "Content-Type: application/json" \
  -d '{"nome":"Produto Seed A Atualizado","descricao":"Descricao A","preco":120.00,"estoque":48,"categoria":"informatica"}'
req "DELETE /produtos/2" -X DELETE "$BASE/produtos/2"
req "GET /usuarios" "$BASE/usuarios"
req "GET /usuarios/1" "$BASE/usuarios/1"
req "POST /usuarios (happy path)" -X POST "$BASE/usuarios" -H "Content-Type: application/json" \
  -d '{"nome":"Fixture User","email":"fixture@example.com","senha":"abc123"}'
req "POST /login (correto)" -X POST "$BASE/login" -H "Content-Type: application/json" \
  -d '{"email":"seed@example.com","senha":"senha123"}'
req "POST /login (senha errada)" -X POST "$BASE/login" -H "Content-Type: application/json" \
  -d '{"email":"seed@example.com","senha":"errada"}'
req "POST /login (tentativa de SQL injection)" -X POST "$BASE/login" -H "Content-Type: application/json" \
  -d "{\"email\":\"' OR '1'='1' -- \",\"senha\":\"qualquer\"}"
req "POST /pedidos (happy path)" -X POST "$BASE/pedidos" -H "Content-Type: application/json" \
  -d '{"usuario_id":1,"itens":[{"produto_id":1,"quantidade":1}]}'
req "GET /pedidos" "$BASE/pedidos"
req "GET /pedidos/usuario/1" "$BASE/pedidos/usuario/1"
req "PUT /pedidos/1/status" -X PUT "$BASE/pedidos/1/status" -H "Content-Type: application/json" \
  -d '{"status":"aprovado"}'
req "GET /relatorios/vendas" "$BASE/relatorios/vendas"
req "POST /admin/query (SQL arbitrario)" -X POST "$BASE/admin/query" -H "Content-Type: application/json" \
  -d '{"sql":"SELECT COUNT(*) FROM produtos"}'
req "POST /admin/reset-db (sem autenticacao)" -X POST "$BASE/admin/reset-db"

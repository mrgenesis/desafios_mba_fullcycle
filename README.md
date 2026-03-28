# Ingestão e Busca Semântica com LangChain e Postgres
**Ingestão**: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
**Busca**: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

## Setup

Copie o arquivo de exemplo para ativar as variáveis de ambientes, e adicine os dados necessários em cada nome.
```bash
cp .env.example .env
```
Instruções para preencher as variáveis de ambiente.
```
OPENAI_API_KEY= # adicione o segredo de autenticação da API OPENAI

MODEL_NAME=gpt-5-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME= # adione um nome para a collection
PDF_PATH= # path comple do documento. exemplo: /mnt/c/users/mrgen/development/ingest_and_search/document.pdf
```


Faça o download das dependências e ative o ambiente virtual.

```bash
python -m venv venv
source venv/bin/activate
# No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

O arquivo docker-compose.yaml, sobe um banco de dados Postgres com o pgVector habilitado.
```bash
docker compose up -d
python src/ingest.py
```

Realize as consultas com o LLM.
```bash
python src/chat.py
```




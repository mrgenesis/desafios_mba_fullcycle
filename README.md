# Ingestão e Busca Semântica com LangChain e Postgres
**Ingestão**: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
**Busca**: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

## Setup

Copie o arquivo de exemplo para ativar as variáveis de ambientes, e adicine os dados necessários em cada nome.
```bash
cp .env.example .env
```

Faça o download das dependências e ative o ambiente virtual.
```bash
python -m venv venv
pip install -r requirements.txt
source venv/bin/activate
# No Windows: venv\Scripts\activate
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




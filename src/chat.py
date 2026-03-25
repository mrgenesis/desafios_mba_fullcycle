from langchain_core.prompts import PromptTemplate
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()



question_user = input("Pergunte alguma coisa: ")
while not question_user.strip():
    print("A pergunta não pode ser vazia. Por favor.")
    question_user = input("Pergunte alguma coisa: ")


t="""
CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question_user}

RESPONDA A "PERGUNTA DO USUÁRIO
"""

embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))

doc_parts_store = PGVector(
    embeddings=embeddings,
    collection_name=os.getenv("PGVECTOR_COLLECTION"),
    connection=os.getenv("PGVECTOR_URL"),
    use_jsonb=True
)

doc_parts = doc_parts_store.similarity_search(question_user, k=2)

context = ""

for i, (doc_part, score) in enumerate(doc_parts):
    context += f"Documento {i+1}, (similaridade: {score:.4f}):\n{doc_part}\n{'-'*80}\n"

template = PromptTemplate(
    input_variables=["context", "question_user"],
    template=t
)

text = template.format(
    context=context, 
    question_user=question_user)
print(text)

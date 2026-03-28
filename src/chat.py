from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from search import get_similar_documents
import os

load_dotenv()

for k in ("OPENAI_API_KEY", "MODEL_NAME"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

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

doc_parts = get_similar_documents(question_user)

context = ""

for i, (doc_part, score) in enumerate(doc_parts, start=1):
    context += f"Documento {i}, (similaridade: {score:.4f}):\n{doc_part.page_content.strip()}\n{'-'*80}\n"

template = PromptTemplate(
    input_variables=["context", "question_user"],
    template=t
)

llm = ChatOpenAI(model=os.getenv("MODEL_NAME"), temperature=0.5)

chain = template | llm

res = chain.invoke({"context": context, "question_user": question_user})
print(res.content)

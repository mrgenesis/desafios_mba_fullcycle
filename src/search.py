from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
for k in ("OPENAI_API_KEY", "EMBEDDING_MODEL", "MODEL_NAME", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL","text-embedding-3-small"))

doc_parts_store = PGVector(
    embeddings=embeddings,
    collection_name=os.getenv("PGVECTOR_COLLECTION"),
    connection=os.getenv("PGVECTOR_URL"),
    use_jsonb=True
)

def get_similar_documents(query: str):
    return doc_parts_store.similarity_search_with_score(query, k=10)
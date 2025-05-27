import os
from langchain_modules.hybrid_retriever import HybridRetriever

GRAPH_CFG = {
    "uri": os.getenv("NEO4J_URI"),
    "username": os.getenv("NEO4J_USERNAME"),
    "password": os.getenv("NEO4J_PASSWORD"),
}

VECTOR_CFG = {
    "index_path": "./data/vector_store/chroma_langchain_db"
}

hybrid_retriever = HybridRetriever(graph_cfg=GRAPH_CFG, vector_cfg=VECTOR_CFG)

def get_bot_response(query: str):
    try:
        results = hybrid_retriever.retrieve(query)
        return results
    except Exception as e:
        print(f"[ERROR] Failed to retrieve response: {e}")
        return []
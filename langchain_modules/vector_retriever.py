from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorRetriever:
    def __init__(self, index_path):
        self.index_path = index_path
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=None)
        self.vector_store = Chroma(persist_directory=self.index_path, embedding_function=self.embeddings)

    def retrieve_similar_messages(self, query, k=5):
        results = self.vector_store.similarity_search(query, k=k)
        return [{
            "content": result.page_content,
            "metadata": result.metadata
        } for result in results]
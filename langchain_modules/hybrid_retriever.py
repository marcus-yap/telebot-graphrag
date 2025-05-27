from graph_retriever import GraphRetriever
from vector_retriever import VectorRetriever

class HybridRetriever:
    def __init__(self, graph_cfg, vector_cfg):
        self.graph_retriever = GraphRetriever(**graph_cfg)
        self.vector_retriever = VectorRetriever(**vector_cfg)

    def retrieve(self, query):
        graph_results = self.graph_retriever.retrieve(query)
        vector_results = self.vector_retriever.retrieve_similar_messages(query)

        seen = set()
        merged = []
        for result in graph_results + vector_results:
            text = result["content"]
            if text not in seen:
                seen.add(text)
                merged.append(result)
        return merged
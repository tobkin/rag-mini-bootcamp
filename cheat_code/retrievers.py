from cheat_code.common_components.vectorizers import Vectorizer
from cheat_code.common_components.vectordb_client_adapters import WcsClientAdapter

class NaiveRetriever:
  
  def __init__(self, vectorizer: Vectorizer):
    self._client_adapter = WcsClientAdapter()
    self._vectorizer = vectorizer
    
  def retrieve(self, query: str) -> str:
    query_vector = self._vectorizer.vectorize_query(query)
    retrieved_chunks_list = self._client_adapter.retrieve(query_vector, k=5)
    formatted_chunks = "\n\n".join(chunk for chunk in retrieved_chunks_list)
    return formatted_chunks
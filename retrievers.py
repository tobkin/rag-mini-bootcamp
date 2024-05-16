from openai import OpenAI
from typing import List
from wcs_client_adapter import WcsClientAdapter

client = OpenAI()

class NaiveRetriever:
  
  def __init__(self, use_wcs_vectorizer: bool, embedding_model=None):
    self._use_wcs_vectorizer = use_wcs_vectorizer
    self._embedding_model = embedding_model
    
  def retrieve(self, query: str) -> str:
    if self._use_wcs_vectorizer:
      formatted_chunks = self._retrieve_by_str(query)
    else:
      formatted_chunks = self._retrieve_by_vector(query)
    return formatted_chunks
  
  def _retrieve_by_str(self, query: str) -> str:
    retrieved_chunks_list = WcsClientAdapter.retrieve_top_k_chunks(query, 5)
    formatted_chunks = "\n\n".join(chunk for chunk in retrieved_chunks_list)
    return formatted_chunks
  
  def _retrieve_by_vector(self, query: str) -> str:
    query_vector = self._vectorize(query)
    retrieved_chunks_list = WcsClientAdapter.retrieve_top_k_chunks_by_vector(query_vector, 5)
    formatted_chunks = "\n\n".join(chunk for chunk in retrieved_chunks_list)
    return formatted_chunks

  def _vectorize(self, query: str) -> List[float]:
    response = client.embeddings.create(
      input=query,
      model=self._embedding_model
    )
    query_vector = response.data[0].embedding
    return query_vector
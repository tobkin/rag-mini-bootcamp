from openai import OpenAI
from typing import List
from wcs_client_adapter import WcsClientAdapter

client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"

class NaiveRetriever:
  
  @staticmethod
  def retrieve(query: str) -> str:
    retrieved_chunks_list = WcsClientAdapter.retrieve_top_k_chunks(query, 5)
    formatted_chunks = "\n\n".join(chunk for chunk in retrieved_chunks_list)
    return formatted_chunks
  
  @staticmethod
  def retrieve_by_vector(query: str) -> str:
    query_vector = NaiveRetriever.vectorize(query)
    retrieved_chunks_list = WcsClientAdapter.retrieve_top_k_chunks_by_vector(query_vector, 5)
    formatted_chunks = "\n\n".join(chunk for chunk in retrieved_chunks_list)
    return formatted_chunks

  @staticmethod
  def vectorize(query: str) -> List[float]:
    response = client.embeddings.create(
      input=query,
      model=EMBEDDING_MODEL
    )
    query_vector = response.data[0].embedding
    return query_vector
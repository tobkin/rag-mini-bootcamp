import os
import weaviate
from typing import List
from weaviate.auth import AuthApiKey
from weaviate.classes import config, data

WCS_URL = os.getenv("WCS_URL")
WCS_API_KEY = os.getenv("WCS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WCS_COLLECTION_NAME = "QaAgentRagChunks"
COLLECTION_TEXT_KEY = "chunk"

class WcsClientAdapter():

  def setup_collection(self) -> None:
    client = self._get_wcs_client() 
    try:
        if client.collections.exists(WCS_COLLECTION_NAME):
            client.collections.delete(WCS_COLLECTION_NAME) 
        
        client.collections.create(
            name=WCS_COLLECTION_NAME,
            properties=[
                config.Property(name=COLLECTION_TEXT_KEY, data_type=config.DataType.TEXT),
                config.Property(name="chunk_index", data_type=config.DataType.INT),
            ]
        )
    finally:
        client.close()
        
  def insert(self, text_splits, text_split_vectors) -> None:
    assert len(text_splits) == len(text_split_vectors)
    client = self._get_wcs_client()  
    chunks_list = []
    for i in range(len(text_splits)):
        data_properties = {
            "chunk": text_splits[i],
            "chunk_index": i
        }
        data_object = data.DataObject(
          properties=data_properties,
          vector=text_split_vectors[i]
        )
        chunks_list.append(data_object)
    try:
      client.collections.get(WCS_COLLECTION_NAME).data.insert_many(chunks_list)
    finally:
      client.close()
  
  def retrieve(self, query_vector: List[float], k: int) -> List[str]:
    client = self._get_wcs_client() 
    try:
      all_chunks = client.collections.get(WCS_COLLECTION_NAME)
      retrieved_chunks = all_chunks.query.near_vector(near_vector=query_vector, limit=k)
      retrieved_chunks_list = [obj.properties['chunk'] for obj in retrieved_chunks.objects]
      return retrieved_chunks_list
    finally:
      client.close()
  
  def count_entries(self) -> int:
      client = self._get_wcs_client() 
      try:
        response = client.collections.get(WCS_COLLECTION_NAME).aggregate.over_all(total_count=True)
        return response.total_count
      finally:
        client.close()

  def _get_wcs_client(self) -> any:
    self._validate_env_variables()
    return weaviate.connect_to_wcs(
            cluster_url = WCS_URL,
            auth_credentials=AuthApiKey(api_key = WCS_API_KEY),
            headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        ) 
  
  def _validate_env_variables(self) -> None:
    required_env_vars = ['WCS_URL', 'WCS_API_KEY']
    for var in required_env_vars:
      if not os.getenv(var):
        raise EnvironmentError(f"Environment variable '{var}' not set. Please ensure it is defined in your .env file.")
    
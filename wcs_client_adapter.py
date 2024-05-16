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

  @staticmethod
  def setup_collection(use_wcs_vectorizer: bool) -> None:
    client = WcsClientAdapter._get_wcs_client() 
    if use_wcs_vectorizer:
      vectorizer = config.Configure.Vectorizer.text2vec_openai()
    else:
      vectorizer = None
      
    try:
        if client.collections.exists(WCS_COLLECTION_NAME):
            client.collections.delete(WCS_COLLECTION_NAME) 
        
        client.collections.create(
            name=WCS_COLLECTION_NAME,
            properties=[
                config.Property(name=COLLECTION_TEXT_KEY, data_type=config.DataType.TEXT),
                config.Property(name="chunk_index", data_type=config.DataType.INT),
            ],
            vectorizer_config=vectorizer
        )
    finally:
        client.close()
        
  @staticmethod
  def insert_text_splits(text_splits) -> None:
    client = WcsClientAdapter._get_wcs_client()
    chunks_list = []
    for i, chunk in enumerate(text_splits):
        data_properties = {
            "chunk": chunk,
            "chunk_index": i
        }
        data_object = data.DataObject(properties=data_properties)
        chunks_list.append(data_object)  
    try:
      client.collections.get(WCS_COLLECTION_NAME).data.insert_many(chunks_list)
    finally:
      client.close()
  
  @staticmethod
  def insert_text_split_vectors(text_splits, text_split_vectors) -> None:
    assert len(text_splits) == len(text_split_vectors)
    client = WcsClientAdapter._get_wcs_client()  
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
  
  @staticmethod   
  def retrieve_top_k_chunks(question: str, k: int) -> List[str]:
    client = WcsClientAdapter._get_wcs_client() 
    try:
      all_chunks = client.collections.get(WCS_COLLECTION_NAME)
      retrieved_chunks = all_chunks.query.near_text(query=question, limit=k)
      retrieved_chunks_list = [obj.properties['chunk'] for obj in retrieved_chunks.objects]
      return retrieved_chunks_list
    finally:
      client.close()
      
  @staticmethod   
  def retrieve_top_k_chunks_by_vector(query_vector: List[float], k: int) -> List[str]:
    client = WcsClientAdapter._get_wcs_client() 
    try:
      all_chunks = client.collections.get(WCS_COLLECTION_NAME)
      retrieved_chunks = all_chunks.query.near_vector(near_vector=query_vector, limit=k)
      retrieved_chunks_list = [obj.properties['chunk'] for obj in retrieved_chunks.objects]
      return retrieved_chunks_list
    finally:
      client.close()
  
  @staticmethod
  def count_entries() -> int:
      client = WcsClientAdapter._get_wcs_client() 
      try:
        response = client.collections.get(WCS_COLLECTION_NAME).aggregate.over_all(total_count=True)
        return response.total_count
      finally:
        client.close()

  @staticmethod
  def _get_wcs_client():
    WcsClientAdapter._validate_env_variables()
    return weaviate.connect_to_wcs(
            cluster_url = WCS_URL,
            auth_credentials=AuthApiKey(api_key = WCS_API_KEY),
            headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        ) 
  
  @staticmethod  
  def _validate_env_variables():
    required_env_vars = ['WCS_URL', 'WCS_API_KEY']
    for var in required_env_vars:
      if not os.getenv(var):
        raise EnvironmentError(f"Environment variable '{var}' not set. Please ensure it is defined in your .env file.")
    
import os
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes import config, data

WCS_URL = os.getenv("WCS_URL")
WCS_API_KEY = os.getenv("WCS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WCS_COLLECTION_NAME = "QaAgentRagChunks"
COLLECTION_TEXT_KEY = "chunk"

class WcsClientAdapter():

  @staticmethod
  def get_wcs_client():
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
    
  @staticmethod
  def setup_collection():
    client = WcsClientAdapter.get_wcs_client() 
    try:
        if client.collections.exists(WCS_COLLECTION_NAME):
            client.collections.delete(WCS_COLLECTION_NAME) 
        
        client.collections.create(
            name=WCS_COLLECTION_NAME,
            properties=[
                config.Property(name=COLLECTION_TEXT_KEY, data_type=config.DataType.TEXT),
                config.Property(name="chunk_index", data_type=config.DataType.INT),
            ],
            vectorizer_config=config.Configure.Vectorizer.text2vec_openai()
        )
    finally:
        client.close()
        
  @staticmethod
  def insert_text_splits(text_splits):
    client = WcsClientAdapter.get_wcs_client()  
    try:
      chunks_list = []
      for i, chunk in enumerate(text_splits):
          data_properties = {
              "chunk": chunk,
              "chunk_index": i
          }
          data_object = data.DataObject(properties=data_properties)
          chunks_list.append(data_object)
      client.collections.get(WCS_COLLECTION_NAME).data.insert_many(chunks_list)
    finally:
      client.close()
  
  @staticmethod   
  def retrieve_top_5_chunks(question):
    client = WcsClientAdapter.get_wcs_client() 
    try:
      top_k = 5
      all_chunks = client.collections.get(WCS_COLLECTION_NAME)
      retrieved_chunks = all_chunks.query.near_text(query=question, limit=top_k)
      retrieved_chunks_list = [obj.properties['chunk'] for obj in retrieved_chunks.objects]
      return retrieved_chunks_list
    finally:
      client.close()
  
  @staticmethod
  def count_entries():
      client = WcsClientAdapter.get_wcs_client() 
      try:
        response = client.collections.get(WCS_COLLECTION_NAME).aggregate.over_all(total_count=True)
        return response.total_count
      finally:
        client.close()
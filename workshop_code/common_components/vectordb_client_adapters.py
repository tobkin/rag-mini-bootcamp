from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Any
from pydantic import BaseModel
import os
import weaviate
from weaviate.auth import AuthApiKey
# from weaviate.classes import config, data
from pinecone import Pinecone
from pinecone import ServerlessSpec

WCS_URL = os.getenv("WCS_URL")
WCS_API_KEY = os.getenv("WCS_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "textsplits"

class VectorDbClientAdapter(ABC):
    @abstractmethod
    def setup_index(self) -> None:
        pass

    @abstractmethod
    def insert(self, text_splits: List[str], text_split_vectors: List[List[float]]) -> None:
        pass

    @abstractmethod
    def retrieve(self, query_vector: List[float], k: int) -> List[str]:
        pass

    @abstractmethod
    def count_entries(self) -> int:
        pass

class PineconeClientAdapter(VectorDbClientAdapter):
  
  def setup_index(self) -> None:
      client = Pinecone(api_key=PINECONE_API_KEY)
      
      if self._index_exists(INDEX_NAME):
        client.delete_index(INDEX_NAME)
      
      client.create_index(
        name=INDEX_NAME,
        dimension=1536, # dimension of text-embedding-3-small output
        metric="cosine",
        spec=ServerlessSpec(
          cloud="aws",
          region="us-east-1"
        )
      )

  def insert(self, text_splits: List[str], text_split_vectors: List[List[float]]) -> None:
    client = Pinecone(api_key=PINECONE_API_KEY)
    index = client.Index(INDEX_NAME)
    vector_objs = []
    for i in range(len(text_splits)):
      obj = {
        "id": f"{i}",
        "values": text_split_vectors[i],
        "metadata": { "text_split": text_splits[i] }
      }
      vector_objs.append(obj)
    index.upsert(vector_objs)

  def retrieve(self, query_vector: List[float], k: int) -> List[str]:
    client = Pinecone(api_key=PINECONE_API_KEY)
    index = client.Index(INDEX_NAME) 
    response = index.query(vector=query_vector, top_k=k, include_metadata=True)
    text_splits = []
    for match in response.get("matches"):
      text_split = match.get("metadata").get("text_split")
      text_splits.append(text_split)
    return text_splits

  def count_entries(self) -> int:
    client = Pinecone(api_key=PINECONE_API_KEY)
    index = client.Index(INDEX_NAME) 
    index_stats = index.describe_index_stats()
    num_entries = index_stats.get("total_vector_count")
    return num_entries
    
  def _index_exists(self, index_name: str) -> bool:
    client = Pinecone(api_key=PINECONE_API_KEY)
    indexes = client.list_indexes()
    for index in indexes:
      if index.get("name") == index_name:
        return True
    return False

class WcsClientAdapter(VectorDbClientAdapter):

  def setup_index(self) -> None:
    client = self._get_wcs_client() 
    try:
        if client.collections.exists(INDEX_NAME):
            client.collections.delete(INDEX_NAME) 
        
        client.collections.create(
            name=INDEX_NAME,
            properties=[
                config.Property(name="chunk", data_type=config.DataType.TEXT),
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
      client.collections.get(INDEX_NAME).data.insert_many(chunks_list)
    finally:
      client.close()
  
  def retrieve(self, query_vector: List[float], k: int) -> List[str]:
    client = self._get_wcs_client() 
    try:
      all_chunks = client.collections.get(INDEX_NAME)
      retrieved_chunks = all_chunks.query.near_vector(near_vector=query_vector, limit=k)
      retrieved_chunks_list = [obj.properties['chunk'] for obj in retrieved_chunks.objects]
      return retrieved_chunks_list
    finally:
      client.close()
  
  def count_entries(self) -> int:
      client = self._get_wcs_client() 
      try:
        response = client.collections.get(INDEX_NAME).aggregate.over_all(total_count=True)
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
    
from __future__ import annotations

import os
import sys
import traceback
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, List

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.exceptions import CouchbaseException
import couchbase.search as search
from couchbase.options import SearchOptions
from couchbase.vector_search import VectorQuery, VectorSearch
from pydantic import BaseModel
from pinecone import Pinecone, ServerlessSpec
import weaviate
from weaviate.auth import AuthApiKey
# from weaviate.classes import config, data

# Couchbase
CB_ENDPOINT=os.getenv("CB_ENDPOINT")
CB_USERNAME=os.getenv("CB_USERNAME")
CB_PASSWORD=os.getenv("CB_PASSWORD")
CB_BUCKET_NAME = "rag-workshop"
CB_SCOPE_NAME = "_default"
CB_COLLECTION_NAME = "_default"
# Weaviate
WCS_URL = os.getenv("WCS_URL")
WCS_API_KEY = os.getenv("WCS_API_KEY")
# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Common
INDEX_NAME = "textsplits"

class VectorDbClientAdapter(ABC):
    @abstractmethod
    def reset_index(self) -> None:
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

# SDK Docs: https://docs.couchbase.com/sdk-api/couchbase-python-client/couchbase_api/couchbase_search.html#
class CouchbaseClientAdapter(VectorDbClientAdapter):
  
    # Capella only supports setting up the index via the cloud console,
    # so unlike other instances of this method, it does not delete and
    # re-setup the index. It only clears the documents in the index.
    def reset_index(self) -> None:
        cluster, collection = self._initialize_cluster()
        try:
            # FIXME: this delete query doesn't work
            # Execute a N1QL query to delete all documents in the collection
            query = f"DELETE FROM `{CB_BUCKET_NAME}`"
            q_res = cluster.query(query)
            
            # status = q_res.metadata().status()
            # print(f"Query status: {status}")
            # print("All documents in the collection have been deleted.")
        except CouchbaseException as e:
            print("Failed to delete documents:", e)
            sys.exit()

    def _initialize_cluster(self):
        try:
            auth = PasswordAuthenticator(CB_USERNAME, CB_PASSWORD)
            options = ClusterOptions(auth)
            options.apply_profile("wan_development")

            cluster = Cluster(CB_ENDPOINT, options)
            cluster.wait_until_ready(timedelta(seconds=5))

            bucket = cluster.bucket(CB_BUCKET_NAME)
            collection = bucket.scope(CB_SCOPE_NAME).collection(CB_COLLECTION_NAME)
            return cluster, collection
        except Exception as e:
            traceback.print_exc()
            sys.exit("Failed to initialize the cluster or collection")

    def insert(self, text_splits: List[str], text_split_vectors: List[List[float]]) -> None:
        vector_objs = []
        for i, text_split in enumerate(text_splits):
            obj = {
                "id": f"{i}",
                "vector_1536_text_embedding_3_small": text_split_vectors[i],
                "text_split": text_split
            }
            vector_objs.append(obj)

        _, collection = self._initialize_cluster()
        try:
            for obj in vector_objs:
                # FIXME: using an upsert instead of an insert because delete query above doesnt work
                # collection.insert(obj["id"], obj)
                collection.upsert(obj["id"], obj)
        except CouchbaseException as e:
            print("Failed to insert document:", e)
            sys.exit()
    
    def retrieve(self, query_vector: List[float], k: int = 4) -> List[Tuple[Document, float]]:
        cluster, collection = self._initialize_cluster()
        bucket = cluster.bucket(CB_BUCKET_NAME)
        scope = bucket.scope(CB_SCOPE_NAME)

        fields = ["*"]

        search_req = search.SearchRequest.create(
            VectorSearch.from_vector_query(
                VectorQuery(
                    'vector_1536_text_embedding_3_small',
                    query_vector,
                    k,
                )
            )
        )
        try:
            search_iter = scope.search(
                index=INDEX_NAME,
                request=search_req,
                options=SearchOptions(
                    limit=k,
                    fields=fields,
                ),
            )

            text_splits = []

            # Parse the results
            for row in search_iter.rows():
                key = row.id
                text_split = collection.get(key).value.get('text_split')
                text_splits.append(text_split)
        except Exception as e:
            raise ValueError(f"Search failed with error: {e}")

        return text_splits

    def count_entries(self) -> int:
        cluster, collection = self._initialize_cluster()
        try:
            query = f"SELECT COUNT(*) AS count FROM `{CB_BUCKET_NAME}`.`{CB_SCOPE_NAME}`.`{CB_COLLECTION_NAME}`"
            result = cluster.query(query)
            count = 0
            for row in result.rows():
                count = row['count']
            return count
        except Exception as e:
            print("Failed to count documents:", e)
            return 0
        
    
class PineconeClientAdapter(VectorDbClientAdapter):
  
  def reset_index(self) -> None:
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

  def reset_index(self) -> None:
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
    
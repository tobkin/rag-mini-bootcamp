from openai import OpenAI

from typing import List

OPENAI_CLIENT = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"

class Vectorizer:
    def vectorize_text_splits(self, text_splits: List[str]) -> List[List[float]]:
        raise NotImplementedError("Implement this method and delete this exception.")
        # response = ???  # TODO: write the API call to the OpenAI Embeddings API
        embeddings = []
        # TODO: build the embeddings list from OpenAI's HTTP response
        return embeddings
    
    def vectorize_query(self, query: str) -> List[float]:
        raise NotImplementedError("Implement this method and delete this exception.")
        # response = ???  # TODO: write the API call to the OpenAI Embeddings API
        query_vector = response.data[0].embedding
        return query_vector
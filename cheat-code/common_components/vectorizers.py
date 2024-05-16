from openai import OpenAI

from typing import List

OPENAI_CLIENT = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"

class Vectorizer:
    def vectorize_text_splits(self, text_splits: List[str]) -> List[List[float]]:
        response = OPENAI_CLIENT.embeddings.create(
            input=text_splits,
            model=EMBEDDING_MODEL
        )
        embeddings = []
        for obj in response.data:
            embeddings.append(obj.embedding)
        return embeddings
    
    def vectorize_query(self, query: str) -> List[float]:
        response = OPENAI_CLIENT.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL
        )
        query_vector = response.data[0].embedding
        return query_vector
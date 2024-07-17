from __future__ import annotations
import json
import random
from pydantic import BaseModel, Field
from typing import List

class EmbeddingData(BaseModel):
    id: int
    vector_1536_text_embedding_3_small: List[float] = Field(..., min_items=1536, max_items=1536)
    text_split: str

def create_embedding_data() -> EmbeddingData:
    embedding_vector = [random.uniform(-1, 1) for _ in range(1536)]
    data = EmbeddingData(
        id=1,
        vector_1536_text_embedding_3_small=embedding_vector,
        text_split="Once upon a time, there was a unicorn"
    )
    return data

def main():
    embedding_data = create_embedding_data()
    data_dict = embedding_data.dict()
    json_data = json.dumps(data_dict, separators=(',', ':'))
    print(json_data)

if __name__ == "__main__":
    main()

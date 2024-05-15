import os
from dotenv import load_dotenv
from indexers import NaiveIndexer
from retrievers import NaiveRetriever
from generators import NaiveGenerator

class NaiveQaRagAgent:
  def __init__(self, doc_uri):
    self._indexer = NaiveIndexer(doc_uri)
    self._retriever = NaiveRetriever()
    self._generator = NaiveGenerator()
    
  def query(self, question):
    retrieved_context = self._retriever.retrieve(question)
    completion = self._generator.get_completion(question, retrieved_context)
    return completion
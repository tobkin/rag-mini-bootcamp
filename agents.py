import os
from dotenv import load_dotenv
from indexers import NaiveIndexer
from retrievers import NaiveWcsRetriever
from generators import Gpt35Generator

class NaiveQaRagAgent:
  def __init__(self, doc_uri):
    self._indexer = NaiveIndexer(doc_uri)
    self._retriever = NaiveWcsRetriever()
    self._generator = Gpt35Generator()
    
  def query(self, question):
    retrieved_context = self._retriever.retrieve(question)
    completion = self._generator.get_completion(question, retrieved_context)
    return completion
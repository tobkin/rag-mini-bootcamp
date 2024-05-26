from workshop_code.common_components.vectorizers import Vectorizer
from workshop_code.indexers import NaiveIndexer
from workshop_code.retrievers import NaiveRetriever
from workshop_code.generators import NaiveGenerator

class NaiveQaRagAgent:
  def __init__(self):
    vectorizer = Vectorizer()
    self._indexer = NaiveIndexer(vectorizer)
    self._retriever = NaiveRetriever(vectorizer)
    self._generator = NaiveGenerator()
    
  def index(self, html_uri: str) -> None:
      self._indexer.index(html_uri)
    
  def query(self, query: str) -> str:
      retrieved_context = self._retrieve(query)
      completion = self._generate(query, retrieved_context)
      return completion
  
  def _retrieve(self, query: str) -> str:
      return self._retriever.retrieve(query)
  
  def _generate(self, query: str, context: str) -> str:
      return self._generator.get_completion(query, context)
  
import os
from dotenv import load_dotenv
from indexers import NaiveWcsIndexer
from retrievers import NaiveWcsRetriever
from generators import Gpt35Generator

class NaiveWcsQaRagAgent:
  def __init__(self, doc_uri):
    self._validate_env_variables()
    self._indexer = NaiveWcsIndexer(doc_uri)
    self._retriever = NaiveWcsRetriever()
    self._generator = Gpt35Generator()
    
  def query(self, question):
    retrieved_context = self._retriever.retrieve(question)
    completion = self._generator.get_completion(question, retrieved_context)
    return completion
  
  def _validate_env_variables(self):
    required_env_vars = ['OPENAI_API_KEY', 'WCS_URL', 'WCS_API_KEY']
    for var in required_env_vars:
      if not os.getenv(var):
        raise EnvironmentError(f"Environment variable '{var}' not set. Please ensure it is defined in your .env file.")
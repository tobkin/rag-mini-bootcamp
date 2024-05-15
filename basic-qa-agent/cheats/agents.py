from indexers import NaiveIndexer
from retrievers import NaiveRetriever
from generators import NaiveGenerator

class NaiveQaHtmlRagAgent:
  """
  A RAG (Retrieval-Augmented Generation) agent designed for question answering
  on a single HTML file.

  This agent can parse an HTML file and provide answers to questions based on 
  the content of that file.

  Methods:
      __init__: Initializes the NaiveQaHtmlRagAgent instance.
      index: Indexes an HTML file.
      delete_index: Deletes the current index.
      query: Processes a query to provide an answer.
      _retrieve: Retrieves context based on a query.
      _generate: Generates an answer based on a query and context.
  """
  def __init__(self):
      self._indexer = NaiveIndexer()
      self._retriever = NaiveRetriever()
      self._generator = NaiveGenerator()
  
  def index(self, html_uri: str) -> None:
      self._indexer.index(html_uri)
  
  def delete_index(self) -> None:
      self._indexer.delete_index()
  
  def query(self, query: str) -> str:
      retrieved_context = self._retrieve(query)
      completion = self._generate(query, retrieved_context)
      return completion
  
  def _retrieve(self, query: str) -> str:
      return self._retriever.retrieve(query)
  
  def _generate(self, query: str, context: str) -> str:
      return self._generator.get_completion(query, context)
  
  def _validate_env_variables(self): # TODO: put into the constructors of the appropriate classes
    required_env_vars = ['OPENAI_API_KEY', 'WCS_URL', 'WCS_API_KEY']
    for var in required_env_vars:
      if not os.getenv(var):
        raise EnvironmentError(f"Environment variable '{var}' not set. Please ensure it is defined in your .env file.")
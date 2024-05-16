from openai import OpenAI
from loaders import DocLoader
from typing import List
from preprocessors import Preprocessor
from text_splitters import SimpleCharacterTextSplitter
from wcs_client_adapter import WcsClientAdapter

client = OpenAI()

CHUNK_SIZE = 250
OVERLAP_SIZE = 25

class NaiveIndexer:

  def __init__(self, use_wcs_vectorizer: bool, embedding_model: str=None):
    self._use_wcs_vectorizer = use_wcs_vectorizer
    self._embedding_model = embedding_model
    self._wcs_client_adapter = WcsClientAdapter(use_wcs_vectorizer)

  def index(self, doc_uri: str):
    if self._use_wcs_vectorizer:
      self._index_with_wcs_vectorizer(doc_uri)
    else:
      self._index_with_vectors(doc_uri)

  def _index_with_wcs_vectorizer(self, doc_uri: str) -> None:
    preprocessor = Preprocessor.get_preprocessor(doc_uri)
    text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    doc_content = DocLoader.load_html(doc_uri)
    cleaned_text = preprocessor.get_text(doc_content)
    text_splits = text_splitter.split_text(cleaned_text)
    self._wcs_client_adapter.setup_collection()
    self._wcs_client_adapter.insert_text_splits(text_splits)
    
  def _index_with_vectors(self, doc_uri: str) -> None:
    preprocessor = Preprocessor.get_preprocessor(doc_uri)
    text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    doc_content = DocLoader.load_html(doc_uri)
    cleaned_text = preprocessor.get_text(doc_content)
    text_splits = text_splitter.split_text(cleaned_text)
    text_split_vectors = self._vectorize(text_splits)
    self._wcs_client_adapter.setup_collection()
    self._wcs_client_adapter.insert_text_split_vectors(text_splits, text_split_vectors) 
    
  def _vectorize(self, text_splits: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
      input=text_splits,
      model=self._embedding_model
    )
    embeddings = []
    for obj in response.data:
      embeddings.append(obj.embedding)
    return embeddings
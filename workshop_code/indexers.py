from workshop_code.indexer_components.loaders import DocLoader
from workshop_code.indexer_components.preprocessors import Preprocessor
from workshop_code.common_components.vectorizers import Vectorizer
from workshop_code.indexer_components.text_splitters import SimpleCharacterTextSplitter
from workshop_code.common_components.vectordb_client_adapters import WcsClientAdapter

CHUNK_SIZE = 250
OVERLAP_SIZE = 25

class NaiveIndexer:

  def __init__(self, vectorizer: Vectorizer):
    self._wcs_client_adapter = WcsClientAdapter()
    self._vectorizer = vectorizer

  def index(self, doc_uri: str) -> None:
    preprocessor = Preprocessor.get_preprocessor(doc_uri)
    text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    doc_content = DocLoader.load_html(doc_uri)
    cleaned_text = preprocessor.get_text(doc_content)
    text_splits = text_splitter.split_text(cleaned_text)
    text_split_vectors = self._vectorizer.vectorize_text_splits(text_splits)
    self._wcs_client_adapter.setup_index()
    self._wcs_client_adapter.insert(text_splits, text_split_vectors) 
    
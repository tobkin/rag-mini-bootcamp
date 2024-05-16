from loaders import DocLoader
from preprocessors import Preprocessor
from text_splitters import SimpleCharacterTextSplitter
from wcs_client_adapter import WcsClientAdapter

CHUNK_SIZE = 150
OVERLAP_SIZE = 25

class NaiveIndexer:

  @staticmethod
  def index(doc_uri: str) -> None:
    preprocessor = Preprocessor.get_preprocessor(doc_uri)
    text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    doc_content = DocLoader.load_html(doc_uri)
    cleaned_text = preprocessor.get_text(doc_content)
    text_splits = text_splitter.split_text(cleaned_text)
    WcsClientAdapter.setup_collection()
    WcsClientAdapter.insert_text_splits(text_splits)
from loaders import DocLoader
from preprocessors import GithubBlogpostPreprocessor, ArxivHtmlPaperPreprocessor
from text_splitters import SimpleCharacterTextSplitter
from wcs_client_adapter import WcsClientAdapter

CHUNK_SIZE = 150
OVERLAP_SIZE = 25
GITHUB_BLOG_POST = "https://lilianweng.github.io/posts/2023-06-23-agent/"
ARXIV_RAG_SURVEY_PAPER = "https://arxiv.org/html/2312.10997v5"

class NaiveIndexer:

  @staticmethod
  def index(doc_uri):
    preprocessor = NaiveIndexer._get_preprocessor(doc_uri)
    text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    doc_content = DocLoader.load_html(doc_uri)
    cleaned_text = preprocessor.get_text(doc_content)
    text_splits = text_splitter.split_text(cleaned_text)
    WcsClientAdapter.setup_collection()
    WcsClientAdapter.insert_text_splits(text_splits)

  @staticmethod
  def _get_preprocessor(doc_uri):
    if doc_uri == GITHUB_BLOG_POST:
      preprocessor = GithubBlogpostPreprocessor()
    elif doc_uri == ARXIV_RAG_SURVEY_PAPER:
      preprocessor = ArxivHtmlPaperPreprocessor()
    else:
      raise ValueError(f"Unsupported document URI: {doc_uri}.") 
    return preprocessor
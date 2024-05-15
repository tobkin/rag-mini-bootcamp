from loaders import HtmlDocumentLoader
from preprocessors import GithubBlogpostPreprocessor, ArxivHtmlPaperPreprocessor
from text_splitters import SimpleCharacterTextSplitter
from wcs_client_adapter import WcsClientAdapter

CACHE_PATH = "./loader_cache"
CHUNK_SIZE = 150
OVERLAP_SIZE = 25
GITHUB_BLOG_POST = "https://lilianweng.github.io/posts/2023-06-23-agent/"
ARXIV_RAG_SURVEY_PAPER = "https://arxiv.org/html/2312.10997v5"

class NaiveWcsIndexer:
  def __init__(self, doc_uri):  # TODO: this calling syntax doesn't make it clear what side effects the constructor has
    
    self._loader = HtmlDocumentLoader(doc_uri, CACHE_PATH)
    if doc_uri == GITHUB_BLOG_POST:
      self._preprocessor = GithubBlogpostPreprocessor()
    elif doc_uri == ARXIV_RAG_SURVEY_PAPER:
      self._preprocessor = ArxivHtmlPaperPreprocessor()
    else:
      raise ValueError(f"Unsupported document URI: {doc_uri}. Expected URIs are GitHub blog post or arXiv RAG survey paper.") 
    self._text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    document_content = self._loader.load()
    cleaned_text = self._preprocessor.get_text(document_content)
    text_splits = self._text_splitter.split_text(cleaned_text)
    WcsClientAdapter.setup_collection()
    WcsClientAdapter.insert_text_splits(text_splits)
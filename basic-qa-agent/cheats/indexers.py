from loaders import DocLoader
from preprocessors import GithubBlogpostPreprocessor, ArxivHtmlPaperPreprocessor
from text_splitters import SimpleCharacterTextSplitter
from wcs_client_adapter import WcsClientAdapter
import os
import hashlib
import requests

CHUNK_SIZE = 150
OVERLAP_SIZE = 25
GITHUB_BLOG_POST = "https://lilianweng.github.io/posts/2023-06-23-agent/"
ARXIV_RAG_SURVEY_PAPER = "https://arxiv.org/html/2312.10997v5"

class NaiveIndexer:
  def __init__(self, doc_uri):  # TODO: this calling syntax doesn't make it clear what side effects the constructor has
    
    self._loader = HtmlDocumentLoader(doc_uri, CACHE_PATH)
    if doc_uri == GITHUB_BLOG_POST:
      self._preprocessor = GithubBlogpostPreprocessor()
    elif doc_uri == ARXIV_RAG_SURVEY_PAPER:
      self._preprocessor = ArxivHtmlPaperPreprocessor()
    else:
      raise ValueError(f"Unsupported document URI: {doc_uri}. Expected URIs are GitHub blog post or arXiv RAG survey paper.") 
    self._text_splitter = SimpleCharacterTextSplitter(CHUNK_SIZE, OVERLAP_SIZE)
    
    def index(self, html_uri):
      document_content = self._loader.load()
      cleaned_text = self._preprocessor.get_text(document_content)
      text_splits = self._text_splitter.split_text(cleaned_text)
      WcsClientAdapter.setup_collection()
      WcsClientAdapter.insert_text_splits(text_splits)
    
    def delete_index(self):
      WcsClientAdapter.delete_index()


class HtmlDocumentLoader:
    """
    A class responsible for loading HTML documents from a specified URI.

    Attributes:
        uri (str): The URI from where the HTML document is loaded.
        cache_path (str): The path to the directory where the loaded documents are cached.
        doc (str): The content of the loaded HTML document as a string.

    Methods:
        load() -> str:
            Loads the HTML document from the specified URI into the `doc` attribute.
            Returns the content of the HTML document as a string.
    """

    def __init__(self):
        """
        Initializes the HtmlDocumentLoader with the specified URI and cache path.

        Args:
            uri (str): The URI from where the HTML document will be loaded.
            cache_path (str): The path to the directory where the loaded documents are cached.
        """
        self.cache_path = "./loader_cache"

    def load(self, uri: str) -> str:
        """
        Loads the HTML document from the specified URI into the `doc` attribute.
        If the document exists in cache, load it from there.

        Args:
            uri (str): The URI of the HTML document to load.

        Returns:
            str: The content of the HTML document.
        """
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        cached_file_path = self._get_cached_file_path(uri)

        if os.path.exists(cached_file_path):
            with open(cached_file_path, 'r', encoding='utf-8') as file:
                doc = file.read()
        else:
            response = requests.get(uri)
            response.raise_for_status()
            doc = response.text

            with open(cached_file_path, 'w', encoding='utf-8') as file:
                file.write(doc)

        return doc

    def _get_cached_file_path(self, uri: str) -> str:
        """
        Computes the cached file path by prepending a four-digit hash to the basename of the URI.

        Args:
            uri (str): The URI of the HTML document.

        Returns:
            str: The full path to the cached file.
        """
        hasher = hashlib.sha256()
        hasher.update(uri.encode('utf-8'))
        hash_prefix = hasher.hexdigest()[:4]

        filename = os.path.basename(uri)
        cached_filename = f"{hash_prefix}_{filename}"

        return os.path.join(self.cache_path, cached_filename)
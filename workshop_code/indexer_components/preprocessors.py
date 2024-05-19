from __future__ import annotations
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, SoupStrainer

GITHUB_BLOG_POST = "https://lilianweng.github.io/posts/2023-06-23-agent/"
ARXIV_RAG_SURVEY_PAPER = "https://arxiv.org/html/2312.10997v5"

class Preprocessor(ABC):
    @abstractmethod
    def get_text(self, html_content: str) -> str:
        pass

    @staticmethod
    def get_preprocessor(doc_uri: str) -> Preprocessor:
        if doc_uri == GITHUB_BLOG_POST:
            preprocessor = GithubBlogpostPreprocessor()
        elif doc_uri == ARXIV_RAG_SURVEY_PAPER:
            preprocessor = ArxivHtmlPaperPreprocessor()
        else:
            raise ValueError(f"Unsupported document URI: {doc_uri}.") 
        return preprocessor

class GithubBlogpostPreprocessor(Preprocessor):
    def get_text(self, html_content: str) -> str:
        """
        Extracts and returns clean text from the post content, title, and header.

        Args:
            html_content (str): The HTML content to process.

        Returns:
            str: Cleaned text from specified parts of the HTML content.
        """
        only_post_text = SoupStrainer(class_=["post-title"]) # TODO: Add the classes to parse here
        soup = BeautifulSoup(html_content, "html.parser", parse_only=only_post_text)
        cleaned_text = soup.get_text()
        return cleaned_text

class ArxivHtmlPaperPreprocessor(Preprocessor):
    def get_text(self, html_content: str) -> str:
        """
        Extracts and returns clean text from the title, authors, affiliations, abstract, and sections.

        Args:
            html_content (str): The HTML content to process.

        Returns:
            str: Cleaned text from specified parts of the HTML content.
        """
        title = self._extract_title(html_content)
        authors_affiliations = self._extract_authors_and_affiliations(html_content)
        abstract = self._extract_abstract(html_content)
        
        sections = []
        for i in range(1, 9):
            section_id = "S" + str(i)
            section_text = self._extract_section_with_subheadings(html_content, section_id)
            sections.append(section_text)

        cleaned_text = title + "\n\n" + authors_affiliations + "\n\n" + abstract + "\n\n" + "\n\n".join(sections)
        return cleaned_text

    def _extract_title(self, html_content: str) -> str:
        return "ArxivHtmlPaperPreprocessor._extract_title() not implemented"
    
    def _extract_authors_and_affiliations(self, html_content: str) -> str:
        return "ArxivHtmlPaperPreprocessor._extract_authors_and_affiliations() not implemented"
    
    def _extract_abstract(self, html_content: str) -> str:
        return "ArxivHtmlPaperPreprocessor._extract_abstracts() not implemented"
    
    def _extract_section_with_subheadings(self, html_content: str, section_id: str) -> str:
        return "ArxivHtmlPaperPreprocessor._extract_section_with_subheadings() not implemented"

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
        only_post_text = SoupStrainer(class_=["post-content", "post-title", "post-header"])
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
        strainer = SoupStrainer('h1', class_="ltx_title ltx_title_document")
        soup = BeautifulSoup(html_content, 'html.parser', parse_only=strainer)
        title_text = soup.get_text()
        return title_text
    
    def _extract_authors_and_affiliations(self, html_content: str) -> str:
        strainer = SoupStrainer('div', class_="ltx_authors")
        soup = BeautifulSoup(html_content, 'html.parser', parse_only=strainer)

        formatted_output = []
        for author in soup.find_all('span', class_='ltx_creator ltx_role_author'):
            name = author.find('span', class_='ltx_personname').get_text(strip=True)
            affiliation = ' '.join(span.get_text(strip=True) for span in author.find_all('span', class_='ltx_contact ltx_role_affiliation'))
            formatted_output.append(f"{name}: {affiliation}\n\n")
        output_text = "\n".join(formatted_output)
        return output_text
    
    def _extract_abstract(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        abstract_div = soup.find('div', class_='ltx_abstract')
        
        if abstract_div:
            abstract_title = abstract_div.find('h6', class_='ltx_title ltx_title_abstract')
            abstract_title_text = abstract_title.get_text(strip=True) if abstract_title else "Abstract"
            
            abstract_paragraph = abstract_div.find('p', class_='ltx_p')
            if abstract_paragraph:
                for footnote in abstract_paragraph.find_all('span', class_='ltx_note'):
                    footnote.decompose()
                
                return f"{abstract_title_text}\n\n{abstract_paragraph.get_text(strip=True)}"
        return "Abstract not found"
    
    def _extract_section_with_subheadings(self, html_content: str, section_id: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        section = soup.find('section', id=section_id)
        
        if section:
            output_text = []
            main_heading = section.find(['h2', 'h3'], class_='ltx_title')
            if main_heading:
                output_text.append(main_heading.get_text(strip=True))
            elements = section.find_all(['p', 'h3'], class_=lambda x: x in ['ltx_p', 'ltx_title ltx_title_subsection'])
            for element in elements:
                if element.name == 'h3':
                    output_text.append("\n\n" + element.get_text(strip=True))
                else:
                    output_text.append(element.get_text(strip=True))
            return '\n\n'.join(output_text)
        return "Section not found"


import json
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import URL_LOGS, CHUNK_OVERLAP, CHUNK_SIZE, SEPARATORS
import re


class Splitter:
    """
    Handles document splitting into chunks and metadata extraction.
    Loads URLs from a JSON log, splits documents using configurable parameters, and extracts metadata like title and
    date from document content.
    """

    def __init__(self):
        """
        Initialize the splitter with URL mappings and text splitting configuration.
        Loads the URL mapping from URL_LOGS/URL_s.json and sets up the RecursiveCharacterTextSplitter with parameters
        from config.
        """
        url_path = URL_LOGS / "URL_s.json"
        with open(url_path, "r") as f:
            self.urls = json.load(f)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            is_separator_regex=True,
            separators=SEPARATORS,
        )
        self.file_type = None

    def get_url(self, file_path) -> str | None:
        """
        Returns the full URL from which the file was downloaded, found in the URL_LOGS dir.
        Returns None if the URL is not found.
        """
        if self.urls:
            for celex_id in self.urls.keys():
                if celex_id in file_path:
                    return self.urls[celex_id]
        return None

    @staticmethod
    def extract_document_date(text: str) -> str:
        """
        Extract the date the document was published. All documents begin with the same form, so search for pattern:
        "of dd Month yyyy".
        :param text: Text to search
        :return: Date of the document in string type
        """
        pattern = r'of\s+(\d{1,2}\s+\w+\s+\d{4})'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return ""

    @staticmethod
    def extract_document_title(text: str) -> str:
        """
        Extract the title of the document. All documents begin with the same form, so search for pattern:
        "Date (in form: dd Month yyyy-) \n on **title of the document** \n THE EUROPEAN PARLIAMENT AND THE COUNCIL"
        :param text: Text to search
        :return: Title of the document in string type
        """
        # Find the date with its surrounding context
        date_pattern = r'of\s+\d{1,2}\s+\w+\s+\d{4}\s*\n'
        date_match = re.search(date_pattern, text)

        if not date_match:
            return ""

        # title starts after the date line
        title_start = date_match.end()

        # Look for the end pattern (case insensitive)
        end_pattern = r'THE EUROPEAN PARLIAMENT AND THE COUNCIL'
        end_match = re.search(end_pattern, text, re.IGNORECASE)

        if not end_match:
            return ""

        title_end = end_match.start()

        # extract the title
        title = text[title_start:title_end].strip()

        # replace newlines and multiple spaces with single space
        title = re.sub(r'\s+', ' ', title)

        # remove any trailing " (Text with EEA relevance)" if present
        title = re.sub(r'\s*\(Text with EEA relevance\)\s*$', '', title)

        return title

    def _get_first_page_text(self, doc_or_text: str | pymupdf.Document) -> str | None:
        """
        Gets the first page text from the document, based on the document file type.
        This function is only used for  metadata extraction. If extraction fails for any reason, it returns None. This
        is by design, as the caller handles None with no problems. Any issues with the nature of the document that
        might raise errors, are handled by the respective splitter.
        :param doc_or_text: the document (pymupdf Document for PDFs) or raw text
        :return: Contents of the first page, or None if extraction fails
        """
        try:
            match self.file_type:
                case "pdf":
                    if not isinstance(doc_or_text, pymupdf.Document):
                        return None
                    if len(doc_or_text) == 0:
                        return None
                    return doc_or_text[0].get_text()
                case "text":
                    if isinstance(doc_or_text, str):
                        return doc_or_text[:2000]
                    return None
                case "html":
                    return None  # To be handled later
                case _:
                    return None
        except Exception:
            return None

    def get_title_date(self, doc_or_text: str | pymupdf.Document) -> tuple[str | None, str | None]:
        """
        Extract title and date from a document's first page.
        :param doc_or_text: The document (pymupdf Document for PDFs) or file path string
        :return: Tuple of (title, date) where each can be None if not found
        """
        first_page_text = self._get_first_page_text(doc_or_text)
        if first_page_text:
            return self.extract_document_title(first_page_text), self.extract_document_date(first_page_text)
        return None, None
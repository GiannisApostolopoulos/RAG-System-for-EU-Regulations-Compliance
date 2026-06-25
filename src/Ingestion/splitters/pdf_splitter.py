
import pymupdf
from splitters.splitter import Splitter
from pathlib import Path
from hashlib import sha256


class PdfSplitter(Splitter):
    """
    Splitter class for processing PDF documents into text chunks.
    Inherits from Splitter and provides specialized functionality for extracting and splitting text content from PDF
    files. Handles page-by-page text extraction, chunking, and metadata association.
    """

    def __init__(self):
        super().__init__()
        self.file_type = "pdf"

    def split(self, pdf_path: str) -> list[dict]:
        """
        Split a PDF document into text chunks with associated metadata.
        Opens a PDF file, extracts text from each page, splits the text into manageable chunks, and creates a list of
        dictionaries containing chunk data along with metadata like URL, date, and title.

        Args:
            pdf_path (str): The file system path to the PDF document to be split.

        Returns:
            list[dict]: A list of dictionaries, each containing:
                - chunk_id (str): SHA256 hash uniquely identifying the chunk
                - page_number (int): The page number the chunk came from
                - chunk_index (int): The index of this chunk within the page
                - chunk_content (str): The actual text content of the chunk
                - URL (str): The URL associated with the document
                - date (str): The date associated with the document
                - title (str): The title of the document
        """
        try:
            pdf_file = pymupdf.open(pdf_path)
        except pymupdf.EmptyFileError as e:
            print(f"File {pdf_path} is empty.")
            raise e
        except pymupdf.FileDataError as e:
            print(f"File {pdf_path} not in PDF format.")
            raise e
        except FileNotFoundError as e:
            print(f"File {pdf_path} not found.")
            raise e
        except Exception as e:
            print(f"Unexpected error trying to split {pdf_path} file.")
            raise e
        url = self.get_url(pdf_path)
        chunks_list = list()

        title, date = self.get_title_date(pdf_file)

        for page_num, page in enumerate(pdf_file, 1):

            try:
                text = page.get_text()
            except RuntimeError as e:
                print(f"Runtime error extracting text from page {page_num}: {e}\n({pdf_path}")
                raise e
            except MemoryError as e:
                print(f"Memory error extracting text from page {page_num}: {e}\n({pdf_path}")
            except Exception as e:
                print(f"Unexpected error extracting text from page {page_num}: {e}\n({pdf_path}")
                raise e

            text = str(text) if text is not None else ""
            chunks = self.text_splitter.split_text(text)

            for chunk_ind, chunk in enumerate(chunks):
                chunk_id_input = f"{pdf_path}|{page_num}|{chunk_ind + 1}"
                chunk_id = sha256(chunk_id_input.encode("utf-8")).hexdigest()

                chunks_list.append(
                    {
                        "chunk_id": chunk_id,
                        "page_number": page_num,
                        "chunk_index": chunk_ind,
                        "chunk_content": chunk,
                        "URL": url,
                        "date": date,
                        "title": title,
                    }
                )

        return chunks_list


if __name__ == "__main__":
    doc = Path(__file__).parent.parent.parent.parent / "docs" / "32022L2555_EN.pdf"
    my_splitter = PdfSplitter()
    chunks = my_splitter.split(str(doc))
    print(len(chunks))
    for chunk in chunks[:5]:
        print(chunk)
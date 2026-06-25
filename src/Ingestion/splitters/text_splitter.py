
from hashlib import sha256
from splitter import Splitter
from langchain_community.document_loaders import TextLoader


class TextSplitter(Splitter):

    def __init__(self):
        super().__init__()
        self.file_type = "text"


    def split(self, file_path, text: str | None):

        if text is None:
            with open(file_path, "r") as f:
                text = f.read()
        url = self.get_url(file_path)
        chunks_list = list()
        chunks = self.text_splitter.split_text(text)

        title, date = self.get_title_date(text)

        for chunk_ind, chunk in enumerate(chunks):

            chunk_id_input = f"{file_path}|{chunk_ind+1}"
            chunk_id = sha256(chunk_id_input.encode("utf-8")).hexdigest()

            chunks_list.append(
                {
                    "chunk_id": chunk_id,
                    "page_number": "Unknown",
                    "chunk_index": chunk_ind,
                    "chunk_content": chunk,
                    "URL": url,
                    "date": date,
                    "title": title,
                }
            )

        return chunks_list
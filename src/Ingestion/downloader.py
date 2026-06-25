
from src.config import DOCS_DIR, URL_LOGS
import requests
from pathlib import Path
from pydantic import BaseModel, field_validator, Field
import json
import os


class Celex(BaseModel):
    """Model for validating CELEX identifier format."""
    celex_id: str = Field(pattern=r"^[A-Z0-9]{10}$")


class Language(BaseModel):
    """Model for validating and normalizing language codes."""
    lang: str = Field(pattern=r"^[A-Z0-9]{2}$")

    @field_validator("lang", mode="before")
    @classmethod
    def cap_lang(cls, l):
        return l.upper()


class Downloader:
    """
    Downloads legal documents from EUR-Lex in various formats.
    Handles file downloading, validation, and metadata tracking for CELEX documents.
    """

    def __init__(self, file_type: str, out_dir: str, lang: str):
        """
        Initialize the downloader with target format, output directory, and language.
        :param file_type: File format to download (supported: 'html', 'txt', 'pdf')
        :param out_dir: Directory where downloaded files will be saved
        :param lang: Two-letter language code ('en', 'fr', 'de' etc)
        """
        self.file_type = file_type
        self.out_dir = out_dir
        self.lang = Language(lang=lang).lang
        self.base_url = f"https://eur-lex.europa.eu/legal-content/{self.lang}/TXT/{self.file_type.upper()}/?uri=CELEX:"
        self.json_file = URL_LOGS / "URL_s.json"

        Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        Path(URL_LOGS).mkdir(parents=True, exist_ok=True)
        Path(self.json_file).touch()

    def _construct_url(self, celex_id: str) -> str:
        """Build the full EUR-Lex download URL for a given CELEX ID."""
        return self.base_url + celex_id + "&qid=1780849928945"

    def _save_file(self, celex_id: str, content: bytes):
        """Save downloaded content to a file with language code in the filename."""
        file_path = self.out_dir / f"{celex_id}_{self.lang}.{self.file_type}"
        file_path.write_bytes(content)

    def _exists(self, celex_id: str) -> bool:
        """
        Check if a file for this CELEX ID and language already exists.
        If the file exists, even with a different extension, we won't download again as the contents are the same.
        :param celex_id: CELEX identifier to check
        :return: True if file exists, False otherwise
        """
        prefix = celex_id + "_" + self.lang
        existing = set([os.path.splitext(name)[0] for name in os.listdir(self.out_dir)])
        return prefix in existing

    def _map_url(self, celex_id: str):
        """
        Save the source URL in a JSON file for metadata tracking.
        Maps CELEX IDs to their source URLs for reference and provenance.
        """
        full_url = self._construct_url(celex_id)
        data = {celex_id: full_url}
        with open(self.json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError as err:
                data = dict()
        data[celex_id] = full_url
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def download(self, celex_id: str):
        """
        Download a document from EUR-Lex by its CELEX identifier.
        Validates the CELEX format, checks for existing files, handles HTTP errors, and saves both the file and URL
        metadata.
        :param celex_id: CELEX identifier of the document to download
        """

        # Validate celex format
        celex_id = Celex(celex_id=celex_id).celex_id

        if self._exists(celex_id):
            print("File already exists, perhaps with another extension.")
            return

        url = self._construct_url(celex_id)
        file_type_end = self.file_type.lower()

        headers = {
            "User-Agent": "Python EUR-Lex downloader/1.0"
        }

        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error")
            print(errh.args[0])
            raise errh
        except requests.exceptions.ReadTimeout as errrt:
            print("Time out")
            raise errrt
        except requests.exceptions.ConnectionError as conerr:
            print("Connection error")
            raise conerr
        except requests.exceptions.RequestException as errex:
            print("Exception request")
            raise errex

        content_type = response.headers.get("Content-Type", "")

        if file_type_end not in content_type.lower():
            print(f"Warning: response may not be in {file_type_end.upper()} format.")

        self._save_file(celex_id, response.content)
        self._map_url(celex_id)


if __name__ == "__main__":
    DOCUMENTS = {
        "GDPR": "32016R0679",
        "DORA": "32022R2554",
        "Data Governance Act": "32022R0868",
        "Data Act": "32023R2854",
        "NIS2": "32022L2555",
        "AI Act": "32024R1689",
        "Open Data Directive": "32019L1024",
    }

    downloader = Downloader(file_type="html", out_dir=DOCS_DIR, lang="en")
    for celex in DOCUMENTS.values():
        downloader.download(celex)
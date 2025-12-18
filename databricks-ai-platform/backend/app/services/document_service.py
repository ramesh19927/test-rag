"""
Document service handles ingestion and parsing of uploaded documents.
In Databricks mode this would write to Unity Catalog / DBFS; locally we persist to disk.
"""
import os
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile

from app.config import Settings
from app.rag.parsers import parse_file


class DocumentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        Path(self.settings.data_root).mkdir(parents=True, exist_ok=True)
        self.raw_dir = Path(self.settings.data_root) / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_dir = Path(self.settings.data_root) / "parsed"
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

    def store_file(self, file: UploadFile) -> Dict[str, Any]:
        ext = Path(file.filename).suffix
        doc_id = f"doc_{uuid.uuid4().hex}"
        path = self.raw_dir / f"{doc_id}{ext}"
        with open(path, "wb") as f:
            f.write(file.file.read())
        return {"document_id": doc_id, "path": str(path)}

    def parse_document(self, document_id: str) -> Dict[str, Any]:
        # locate file
        matches = list(self.raw_dir.glob(f"{document_id}.*"))
        if not matches:
            raise FileNotFoundError(f"Document {document_id} not found")
        file_path = matches[0]
        text = parse_file(file_path)
        parsed_path = self.parsed_dir / f"{document_id}.txt"
        parsed_path.write_text(text)
        return {"document_id": document_id, "text": text, "path": str(parsed_path)}

"""Module 1: Document Loader.

Responsible for reading corpus files from disk, assigning integer doc IDs
in sorted-filename order for reproducible results, and returning Document objects.
"""

from dataclasses import dataclass
import os
from typing import Dict


@dataclass(frozen=True)
class Document:
    """Represents a document in the search corpus."""
    doc_id: int
    filename: str
    text: str


def load_documents(folder: str) -> Dict[int, Document]:
    """Load text documents from the specified directory.

    Args:
        folder: Path to directory containing document files (.txt).

    Returns:
        dict[int, Document]: Mapping of integer doc_id to Document object.

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        ValueError: If folder is not a directory or contains no valid documents.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Corpus folder '{folder}' does not exist.")
    if not os.path.isdir(folder):
        raise ValueError(f"Path '{folder}' is not a directory.")

    documents: Dict[int, Document] = {}
    filenames = sorted(os.listdir(folder))
    next_id = 0

    for fname in filenames:
        if not fname.lower().endswith(".txt"):
            continue

        file_path = os.path.join(folder, fname)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
        except Exception:
            continue

        # Skip empty documents
        if not content:
            continue

        documents[next_id] = Document(doc_id=next_id, filename=fname, text=content)
        next_id += 1

    if not documents:
        raise ValueError(f"No non-empty .txt documents found in '{folder}'.")

    return documents


"""Module 4: Inverted Index.

Responsible for building and storing the inverted index, mapping terms
to sorted postings lists of document IDs. Maintains the universe of all document IDs.
"""

from typing import Dict, Iterable, List, Optional, Set
import json
import pickle


class InvertedIndex:
    """Inverted Index storing term -> sorted list of doc IDs, plus position info."""

    def __init__(self) -> None:
        # Internal temporary collection during build: term -> set of doc_ids
        self._temp_index: Dict[str, Set[int]] = {}
        # Finalized index: term -> sorted list of doc_ids
        self._index: Dict[str, List[int]] = {}
        # Optional positional index: term -> {doc_id: [positions]}
        self._positional_index: Dict[str, Dict[int, List[int]]] = {}
        # Complete universe of document IDs
        self._doc_ids: Set[int] = set()
        self._is_finalized: bool = False

    def add_document(self, doc_id: int, terms: Iterable[str]) -> None:
        """Add normalized terms for a document to the index.

        Args:
            doc_id: Unique integer document identifier.
            terms: Iterable of normalized term strings.
        """
        self._doc_ids.add(doc_id)
        self._is_finalized = False

        for term in terms:
            if term not in self._temp_index:
                self._temp_index[term] = set()
            self._temp_index[term].add(doc_id)

    def add_document_with_positions(self, doc_id: int, term_positions: Iterable[tuple]) -> None:
        """Add terms with positions for a document (supports phrase queries).

        Args:
            doc_id: Unique integer document identifier.
            term_positions: Iterable of (term, pos) tuples.
        """
        self._doc_ids.add(doc_id)
        self._is_finalized = False

        for term, pos in term_positions:
            if term not in self._temp_index:
                self._temp_index[term] = set()
            self._temp_index[term].add(doc_id)

            if term not in self._positional_index:
                self._positional_index[term] = {}
            if doc_id not in self._positional_index[term]:
                self._positional_index[term][doc_id] = []
            self._positional_index[term][doc_id].append(pos)

    def finalize(self) -> None:
        """Convert temporary set-based postings into sorted lists for fast merging."""
        self._index = {term: sorted(doc_set) for term, doc_set in self._temp_index.items()}
        self._is_finalized = True

    def get_postings(self, term: str) -> List[int]:
        """Retrieve the sorted postings list for a term.

        Args:
            term: Normalized term string.

        Returns:
            Sorted list of document IDs containing the term.
        """
        if not self._is_finalized:
            self.finalize()
        return self._index.get(term, [])

    def get_positions(self, term: str, doc_id: int) -> List[int]:
        """Retrieve positions of a term in a specific document."""
        return self._positional_index.get(term, {}).get(doc_id, [])

    def vocabulary(self) -> Set[str]:
        """Get the complete set of indexed terms."""
        if self._is_finalized:
            return set(self._index.keys())
        return set(self._temp_index.keys())

    def all_doc_ids(self) -> List[int]:
        """Return all document IDs in sorted order (needed for NOT queries)."""
        return sorted(self._doc_ids)

    def doc_frequency(self, term: str) -> int:
        """Return the number of documents containing the term."""
        return len(self.get_postings(term))

    def total_documents(self) -> int:
        """Return total count of documents in the collection."""
        return len(self._doc_ids)

    def save(self, filepath: str, as_json: bool = False) -> None:
        """Serialize index to disk."""
        if not self._is_finalized:
            self.finalize()
        data = {
            "index": self._index,
            "positional_index": self._positional_index,
            "doc_ids": list(self._doc_ids),
        }
        if as_json:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)

    def load(self, filepath: str, as_json: bool = False) -> None:
        """Load index from disk."""
        if as_json:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
        self._index = {k: list(v) for k, v in data["index"].items()}
        self._positional_index = {
            k: {int(doc_id): positions for doc_id, positions in v.items()}
            for k, v in data.get("positional_index", {}).items()
        }
        self._doc_ids = set(data["doc_ids"])
        self._temp_index = {k: set(v) for k, v in self._index.items()}
        self._is_finalized = True


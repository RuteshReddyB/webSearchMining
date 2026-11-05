"""Search Engine Facade.

Ties together document loading, tokenization, normalization, inverted index,
wildcard indexing, query processing, and snippet extraction into a clean API.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional
import re

from src.document_loader import Document, load_documents
from src.tokenizer import tokenize_with_positions
from src.normalizer import normalize_term
from src.inverted_index import InvertedIndex
from src.wildcard import WildcardIndex
from src.query_processor import QueryProcessor, QueryError


@dataclass
class SearchHit:
    """Represents a single matching document result."""
    doc_id: int
    filename: str
    snippet: str


@dataclass
class SearchResult:
    """Represents the complete result of a search query."""
    query: str
    hits: List[SearchHit] = field(default_factory=list)
    elapsed_ms: float = 0.0
    total_docs: int = 0
    matched_terms: List[str] = field(default_factory=list)


class SearchEngine:
    """Facade for the Information Retrieval Engine."""

    def __init__(self, corpus_folder: str, remove_stop_words: bool = False) -> None:
        self.corpus_folder = corpus_folder
        self.remove_stop_words = remove_stop_words
        self.documents: Dict[int, Document] = {}
        self.index = InvertedIndex()
        self.wildcard_index = WildcardIndex(k=2)
        self.query_processor: Optional[QueryProcessor] = None

        self._build()

    def _build(self) -> None:
        """Load corpus, index documents, and construct wildcard index."""
        self.documents = load_documents(self.corpus_folder)

        for doc_id, doc in self.documents.items():
            raw_tokens_pos = tokenize_with_positions(doc.text)
            term_positions = []
            for raw_tok, pos in raw_tokens_pos:
                term = normalize_term(raw_tok, remove_stop_words=self.remove_stop_words)
                if term:
                    term_positions.append((term, pos))

            self.index.add_document_with_positions(doc_id, term_positions)

        self.index.finalize()
        self.wildcard_index.build(self.index.vocabulary())

        self.query_processor = QueryProcessor(
            get_postings_fn=self.index.get_postings,
            all_doc_ids_fn=self.index.all_doc_ids,
            expand_wildcard_fn=self.wildcard_index.expand,
        )

    def get_document(self, doc_id: int) -> Optional[Document]:
        """Retrieve a document by its doc_id."""
        return self.documents.get(doc_id)

    def _extract_query_words(self, query: str) -> List[str]:
        """Extract all content terms / expanded terms from the query for snippet generation."""
        tokens = QueryProcessor.tokenize_query(query)
        words = []
        for t in tokens:
            if t in {"AND", "OR", "NOT", "(", ")"}:
                continue
            norm = normalize_term(t)
            if not norm:
                continue
            if "*" in norm or "?" in norm:
                words.extend(self.wildcard_index.expand(norm))
            else:
                words.append(norm)
        return list(set(words))

    def _generate_snippet(self, text: str, query_words: List[str], max_length: int = 160) -> str:
        """Generate a contextual snippet highlighting the first occurrence of any query word."""
        if not text:
            return ""

        lower_text = text.lower()
        earliest_pos = -1

        for word in query_words:
            if not word:
                continue
            pos = lower_text.find(word.lower())
            if pos != -1:
                if earliest_pos == -1 or pos < earliest_pos:
                    earliest_pos = pos

        if earliest_pos == -1:
            # No direct word match (e.g. from NOT queries or pure wildcard)
            snippet = text[:max_length].strip()
            return snippet + "..." if len(text) > max_length else snippet

        # Center window around the earliest match
        start = max(0, earliest_pos - 40)
        end = min(len(text), earliest_pos + max_length - 40)

        snippet = text[start:end].strip()
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{snippet}{suffix}"

    def search(self, query: str) -> SearchResult:
        """Execute a Boolean search with wildcard expansion.

        Args:
            query: Query string like 'comp* AND NOT (network OR data)'.

        Returns:
            SearchResult containing hits, timing, and statistics.
        """
        if not query or not query.strip():
            return SearchResult(query=query, hits=[], elapsed_ms=0.0, total_docs=len(self.documents))

        start_time = time.perf_counter()
        doc_ids = self.query_processor.execute(query)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        query_words = self._extract_query_words(query)

        hits: List[SearchHit] = []
        for doc_id in doc_ids:
            doc = self.documents.get(doc_id)
            if not doc:
                continue
            snippet = self._generate_snippet(doc.text, query_words)
            hits.append(SearchHit(doc_id=doc.doc_id, filename=doc.filename, snippet=snippet))

        return SearchResult(
            query=query,
            hits=hits,
            elapsed_ms=elapsed_ms,
            total_docs=len(self.documents),
            matched_terms=query_words,
        )


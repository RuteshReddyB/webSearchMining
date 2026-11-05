"""Module 6: Wildcard.

Implements k-gram (bigram) index over vocabulary terms with regex post-filtering.
Supports arbitrary wildcard patterns (* and ?) anywhere in the term:
- Prefix (comp*)
- Suffix (*tion)
- Middle (c*t, h?llo)
- Multiple wildcards (p*t*n, *a*b*)
"""

import re
from typing import Dict, Iterable, List, Set


class WildcardIndex:
    """Bigram index for wildcard term expansion with post-filtering."""

    def __init__(self, k: int = 2) -> None:
        self.k: int = k
        self.bigram_index: Dict[str, Set[str]] = {}
        self.vocabulary: Set[str] = set()

    def build(self, vocabulary: Iterable[str]) -> None:
        """Build the k-gram index from the given vocabulary."""
        self.bigram_index.clear()
        self.vocabulary = set(vocabulary)

        for term in self.vocabulary:
            padded = f"${term}$"
            for i in range(len(padded) - self.k + 1):
                gram = padded[i : i + self.k]
                if gram not in self.bigram_index:
                    self.bigram_index[gram] = set()
                self.bigram_index[gram].add(term)

    def _extract_grams_from_pattern(self, pattern: str) -> List[str]:
        """Extract all valid k-grams from constant segments of the padded pattern.

        Example:
            'comp*' -> padded '$comp*' -> segment '$comp' -> grams ['$c', 'co', 'om', 'mp']
            '*tion' -> padded '*tion$' -> segment 'tion$' -> grams ['ti', 'io', 'on', 'n$']
            'c*t'   -> padded '$c*t$'   -> segments '$c', 't$' -> grams ['$c', 't$']
        """
        # Split pattern by wildcard characters (* and ?)
        # But we must preserve the start ($) and end ($) anchors
        padded = f"${pattern}$"
        # Split on * and ?
        segments = re.split(r"[\*\?]+", padded)
        grams = []
        for seg in segments:
            if len(seg) >= self.k:
                for i in range(len(seg) - self.k + 1):
                    grams.append(seg[i : i + self.k])
        return grams

    @staticmethod
    def _pattern_to_regex(pattern: str) -> re.Pattern:
        """Convert a wildcard pattern with * and ? to an anchored compiled regex."""
        # Escape special regex characters except * and ?
        parts = []
        for char in pattern:
            if char == "*":
                parts.append(".*")
            elif char == "?":
                parts.append(".")
            else:
                parts.append(re.escape(char))
        regex_str = f"^{''.join(parts)}$"
        return re.compile(regex_str)

    def expand(self, pattern: str) -> List[str]:
        """Expand a wildcard pattern into all matching vocabulary terms.

        Args:
            pattern: Wildcard query pattern (casefolded).

        Returns:
            Sorted list of matching terms from the vocabulary.
        """
        if not pattern:
            return []

        # If no wildcards present, return exact match if in vocabulary
        if "*" not in pattern and "?" not in pattern:
            return [pattern] if pattern in self.vocabulary else []

        regex = self._pattern_to_regex(pattern)
        grams = self._extract_grams_from_pattern(pattern)

        # Candidate filtering using k-gram intersection
        if grams:
            # Sort grams by posting frequency for faster intersection
            grams_sorted = sorted(grams, key=lambda g: len(self.bigram_index.get(g, set())))
            candidates = set(self.bigram_index.get(grams_sorted[0], set()))
            for g in grams_sorted[1:]:
                candidates &= self.bigram_index.get(g, set())
                if not candidates:
                    break
        else:
            # Edge case: Pattern like "*" or "?" or "?*" with no usable bigrams.
            # Fall back to scanning the entire vocabulary.
            candidates = self.vocabulary

        # Post-filter candidates with compiled regex
        matches = [term for term in candidates if regex.match(term)]
        return sorted(matches)


"""Module 3: Normalizer.

Responsible for turning tokens into index terms.
Applies Unicode case-folding (str.casefold()), optional punctuation cleaning,
and handles wildcard pattern normalization without stripping pattern symbols.
"""

from typing import Iterable, List, Optional, Set

# Standard English stop words (can be enabled if needed; default off or configurable)
DEFAULT_STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}


def normalize_term(term: str, remove_stop_words: bool = False, stop_words: Optional[Set[str]] = None) -> Optional[str]:
    """Normalize a single token or query term.

    Steps:
    1. Case folding using str.casefold() (e.g. handles German 'STRASSE' -> 'strasse', 'Apple' -> 'apple').
    2. Strip leading/trailing non-alphanumeric chars except wildcard symbols '*' and '?'.
    3. Optional stop-word filtering.

    Args:
        term: Input token string.
        remove_stop_words: Whether to filter out stop words.
        stop_words: Custom set of stop words; defaults to DEFAULT_STOP_WORDS if None.

    Returns:
        Normalized term string or None if filtered out.
    """
    if term is None:
        return None

    # Strip whitespace and apply full Unicode case folding
    folded = term.strip().casefold()
    if not folded:
        return None

    # If stop-word removal is active and this is an exact match (without wildcards)
    if remove_stop_words and "*" not in folded and "?" not in folded:
        sw = stop_words if stop_words is not None else DEFAULT_STOP_WORDS
        if folded in sw:
            return None

    return folded


def normalize_all(tokens: Iterable[str], remove_stop_words: bool = False, stop_words: Optional[Set[str]] = None) -> List[str]:
    """Normalize a sequence of tokens into index terms.

    Args:
        tokens: Iterable of token strings.
        remove_stop_words: Whether to filter out stop words.
        stop_words: Custom set of stop words.

    Returns:
        List of non-None normalized terms.
    """
    normalized: List[str] = []
    for tok in tokens:
        term = normalize_term(tok, remove_stop_words=remove_stop_words, stop_words=stop_words)
        if term:
            normalized.append(term)
    return normalized


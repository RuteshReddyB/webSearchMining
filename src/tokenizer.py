"""Module 2: Tokenizer.

Responsible for splitting raw text into raw tokens according to documented rules.
Does NOT perform lowercasing (which belongs to the normalizer module).
"""

import re
from typing import List, Tuple

# Token pattern matching alphanumeric sequences with optional trailing contractions (e.g., don't, state's)
# Hyphenated words are split into separate tokens so sub-words can be indexed cleanly.
TOKEN_REGEX = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")


def tokenize(text: str) -> List[str]:
    """Tokenize input text into a list of raw token strings without case modifications.

    Tokenization rules:
    - Alphanumeric chunks are kept together.
    - Contractions like "don't" or "user's" are preserved as single tokens.
    - Hyphens and punctuation are treated as word separators.
    - Pure punctuation symbols are discarded.

    Args:
        text: Raw input string.

    Returns:
        List of raw token strings.
    """
    if not text:
        return []
    return TOKEN_REGEX.findall(text)


def tokenize_with_positions(text: str) -> List[Tuple[str, int]]:
    """Tokenize input text and return each token alongside its 0-based word position.

    Args:
        text: Raw input string.

    Returns:
        List of tuples (token_string, position_index).
    """
    tokens = tokenize(text)
    return [(tok, idx) for idx, tok in enumerate(tokens)]


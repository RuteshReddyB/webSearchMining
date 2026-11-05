"""Unit tests for Module 3: Normalizer."""

import unittest
from src.normalizer import normalize_term, normalize_all


class TestNormalizer(unittest.TestCase):

    def test_case_folding(self):
        self.assertEqual(normalize_term("Apple"), "apple")
        self.assertEqual(normalize_term("COMPUTER"), "computer")

    def test_unicode_case_folding(self):
        # German double-s (Eszett) case folds to 'ss'
        self.assertEqual(normalize_term("STRASSE"), "strasse")
        self.assertEqual(normalize_term("Straße"), "strasse")

    def test_wildcard_preservation(self):
        # Wildcard symbols * and ? must NOT be stripped or removed
        self.assertEqual(normalize_term("Comp*"), "comp*")
        self.assertEqual(normalize_term("H?llo"), "h?llo")
        self.assertEqual(normalize_term("*TION"), "*tion")
        self.assertEqual(normalize_term("c*t?"), "c*t?")

    def test_stop_words_toggle(self):
        # When disabled (default)
        self.assertEqual(normalize_term("the", remove_stop_words=False), "the")
        # When enabled
        self.assertIsNone(normalize_term("the", remove_stop_words=True))
        self.assertEqual(normalize_term("computer", remove_stop_words=True), "computer")

    def test_normalize_all(self):
        tokens = ["The", "Apple", "is", "DELICIOUS"]
        terms = normalize_all(tokens, remove_stop_words=False)
        self.assertEqual(terms, ["the", "apple", "is", "delicious"])

        filtered = normalize_all(tokens, remove_stop_words=True)
        self.assertEqual(filtered, ["apple", "delicious"])


if __name__ == "__main__":
    unittest.main()


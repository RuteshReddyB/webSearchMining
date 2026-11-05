"""Unit tests for Module 2: Tokenizer."""

import unittest
from src.tokenizer import tokenize, tokenize_with_positions


class TestTokenizer(unittest.TestCase):

    def test_basic_tokenization(self):
        text = "Hello, World!"
        tokens = tokenize(text)
        self.assertEqual(tokens, ["Hello", "World"])

    def test_contractions(self):
        text = "Don't leave without the user's permission."
        tokens = tokenize(text)
        self.assertEqual(tokens, ["Don't", "leave", "without", "the", "user's", "permission"])

    def test_hyphenated_words(self):
        text = "State-of-the-art information retrieval system."
        tokens = tokenize(text)
        self.assertEqual(tokens, ["State", "of", "the", "art", "information", "retrieval", "system"])

    def test_numbers_and_alphanumerics(self):
        text = "Python 3.11 was released in 2022 with 500k downloads."
        tokens = tokenize(text)
        self.assertEqual(tokens, ["Python", "3", "11", "was", "released", "in", "2022", "with", "500k", "downloads"])

    def test_empty_and_whitespace(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   \n\t  "), [])

    def test_tokenize_with_positions(self):
        text = "quick brown fox"
        tokens_pos = tokenize_with_positions(text)
        self.assertEqual(tokens_pos, [("quick", 0), ("brown", 1), ("fox", 2)])


if __name__ == "__main__":
    unittest.main()


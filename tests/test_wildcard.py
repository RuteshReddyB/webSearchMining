"""Unit tests for Module 6: Wildcard."""

import unittest
from src.wildcard import WildcardIndex


class TestWildcardIndex(unittest.TestCase):

    def setUp(self):
        self.vocab = [
            "computer",
            "computation",
            "computing",
            "communication",
            "action",
            "caption",
            "cat",
            "chat",
            "cost",
            "data",
            "date",
            "hello",
            "hallo",
            "network",
            "networking",
        ]
        self.wildcard = WildcardIndex(k=2)
        self.wildcard.build(self.vocab)

    def test_prefix_wildcard(self):
        res = self.wildcard.expand("comp*")
        self.assertEqual(res, ["computation", "computer", "computing"])

    def test_suffix_wildcard(self):
        res = self.wildcard.expand("*tion")
        self.assertEqual(res, ["action", "caption", "communication", "computation"])

    def test_middle_wildcard(self):
        res = self.wildcard.expand("c*t")
        self.assertEqual(res, ["cat", "chat", "cost"])

    def test_single_char_wildcard(self):
        res = self.wildcard.expand("h?llo")
        self.assertEqual(res, ["hallo", "hello"])

        res2 = self.wildcard.expand("dat?")
        self.assertEqual(res2, ["data", "date"])

    def test_multiple_wildcards(self):
        res = self.wildcard.expand("c*m*n")
        self.assertEqual(res, ["communication", "computation"])

    def test_no_match(self):
        res = self.wildcard.expand("xyz*")
        self.assertEqual(res, [])

    def test_exact_match_no_wildcards(self):
        self.assertEqual(self.wildcard.expand("network"), ["network"])
        self.assertEqual(self.wildcard.expand("unknown"), [])

    def test_star_alone(self):
        res = self.wildcard.expand("*")
        self.assertEqual(len(res), len(self.vocab))


if __name__ == "__main__":
    unittest.main()


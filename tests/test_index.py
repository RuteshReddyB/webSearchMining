"""Unit tests for Module 4: Inverted Index."""

import unittest
import tempfile
import os
from src.inverted_index import InvertedIndex


class TestInvertedIndex(unittest.TestCase):

    def setUp(self):
        self.idx = InvertedIndex()
        # Doc 0: apple banana cherry
        self.idx.add_document(0, ["apple", "banana", "cherry"])
        # Doc 1: apple cherry date
        self.idx.add_document(1, ["apple", "cherry", "date"])
        # Doc 2: banana fig grape
        self.idx.add_document(2, ["banana", "fig", "grape"])
        self.idx.finalize()

    def test_postings(self):
        self.assertEqual(self.idx.get_postings("apple"), [0, 1])
        self.assertEqual(self.idx.get_postings("banana"), [0, 2])
        self.assertEqual(self.idx.get_postings("cherry"), [0, 1])
        self.assertEqual(self.idx.get_postings("date"), [1])
        self.assertEqual(self.idx.get_postings("fig"), [2])
        self.assertEqual(self.idx.get_postings("nonexistent"), [])

    def test_vocabulary_and_doc_ids(self):
        vocab = self.idx.vocabulary()
        self.assertIn("apple", vocab)
        self.assertIn("grape", vocab)
        self.assertEqual(self.idx.all_doc_ids(), [0, 1, 2])
        self.assertEqual(self.idx.total_documents(), 3)

    def test_doc_frequency(self):
        self.assertEqual(self.idx.doc_frequency("apple"), 2)
        self.assertEqual(self.idx.doc_frequency("nonexistent"), 0)

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.idx.save(tmp_path, as_json=True)
            loaded_idx = InvertedIndex()
            loaded_idx.load(tmp_path, as_json=True)

            self.assertEqual(loaded_idx.get_postings("apple"), [0, 1])
            self.assertEqual(loaded_idx.all_doc_ids(), [0, 1, 2])
            self.assertEqual(loaded_idx.vocabulary(), self.idx.vocabulary())
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()


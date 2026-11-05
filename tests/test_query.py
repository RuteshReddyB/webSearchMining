"""Unit tests for Module 5: Query Processor."""

import unittest
from src.query_processor import QueryProcessor, QueryError
from src.inverted_index import InvertedIndex
from src.wildcard import WildcardIndex


class TestQueryProcessor(unittest.TestCase):

    def setUp(self):
        self.idx = InvertedIndex()
        # Doc 0: computer science information
        self.idx.add_document(0, ["computer", "science", "information"])
        # Doc 1: information retrieval science
        self.idx.add_document(1, ["information", "retrieval", "science"])
        # Doc 2: computer network communication
        self.idx.add_document(2, ["computer", "network", "communication"])
        # Doc 3: computation and algorithms
        self.idx.add_document(3, ["computation", "algorithms"])
        self.idx.finalize()

        self.wildcard = WildcardIndex(k=2)
        self.wildcard.build(self.idx.vocabulary())

        self.qp = QueryProcessor(
            get_postings_fn=self.idx.get_postings,
            all_doc_ids_fn=self.idx.all_doc_ids,
            expand_wildcard_fn=self.wildcard.expand,
        )

    def test_single_term(self):
        self.assertEqual(self.qp.execute("computer"), [0, 2])
        self.assertEqual(self.qp.execute("science"), [0, 1])
        self.assertEqual(self.qp.execute("nonexistent"), [])

    def test_boolean_and(self):
        # computer AND science -> Doc 0
        self.assertEqual(self.qp.execute("computer AND science"), [0])
        # information AND science -> Doc 0, 1
        self.assertEqual(self.qp.execute("information AND science"), [0, 1])

    def test_boolean_or(self):
        # retrieval OR communication -> Doc 1, 2
        self.assertEqual(self.qp.execute("retrieval OR communication"), [1, 2])

    def test_boolean_not(self):
        # NOT computer -> [1, 3]
        self.assertEqual(self.qp.execute("NOT computer"), [1, 3])

    def test_and_not(self):
        # computer AND NOT network -> [0]
        self.assertEqual(self.qp.execute("computer AND NOT network"), [0])

    def test_parentheses_and_precedence(self):
        # (computer OR retrieval) AND science -> Doc 0, 1
        self.assertEqual(self.qp.execute("(computer OR retrieval) AND science"), [0, 1])
        # Precedence check: NOT > AND > OR
        # retrieval OR computer AND science == retrieval OR (computer AND science) -> [1] OR [0] -> [0, 1]
        self.assertEqual(self.qp.execute("retrieval OR computer AND science"), [0, 1])

    def test_implicit_and(self):
        # "computer science" -> "computer AND science"
        self.assertEqual(self.qp.execute("computer science"), [0])

    def test_wildcard_in_boolean(self):
        # comp* matches 'computer' and 'computation'
        # comp* -> [0, 2, 3]
        self.assertEqual(self.qp.execute("comp*"), [0, 2, 3])
        # comp* AND science -> [0]
        self.assertEqual(self.qp.execute("comp* AND science"), [0])
        # comp* AND NOT network -> [0, 3]
        self.assertEqual(self.qp.execute("comp* AND NOT network"), [0, 3])

    def test_error_handling(self):
        # Empty query
        self.assertEqual(self.qp.execute(""), [])
        self.assertEqual(self.qp.execute("   "), [])

        # Dangling operator
        with self.assertRaises(QueryError):
            self.qp.execute("computer AND")

        with self.assertRaises(QueryError):
            self.qp.execute("AND computer")

        with self.assertRaises(QueryError):
            self.qp.execute("computer AND AND science")

        # Unbalanced parentheses
        with self.assertRaises(QueryError):
            self.qp.execute("(computer OR science")

        with self.assertRaises(QueryError):
            self.qp.execute("computer OR science)")


if __name__ == "__main__":
    unittest.main()


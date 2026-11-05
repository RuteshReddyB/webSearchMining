"""Unit tests for Module 7: GUI behaviors."""

import unittest
import tkinter as tk
from src.gui import SearchApp
from src.search_engine import SearchEngine


class TestGUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = SearchEngine("data/documents")

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.app = SearchApp(self.root, self.engine)

    def tearDown(self):
        self.root.destroy()

    def test_results_widget_is_disabled_read_only(self):
        """Verify ScrolledText state is 'disabled' so user cannot type into it."""
        self.assertEqual(self.app.results_text.cget("state"), "disabled")
        # Attempt to insert directly
        before = self.app.results_text.get("1.0", tk.END)
        self.app.results_text.insert("1.0", "Hacked text")
        after = self.app.results_text.get("1.0", tk.END)
        self.assertEqual(before, after)

    def test_search_replaces_results_not_appends(self):
        """Verify repeated searches replace previous contents instead of appending."""
        self.app.query_var.set("computer")
        self.app.perform_search()
        text_first = self.app.results_text.get("1.0", tk.END)
        self.assertIn("computer", text_first.lower())

        self.app.query_var.set("python")
        self.app.perform_search()
        text_second = self.app.results_text.get("1.0", tk.END)
        self.assertIn("python", text_second.lower())
        self.assertNotIn("doc01_computer_science.txt", text_second)

    def test_empty_query_message(self):
        """Verify searching empty query provides a clean message."""
        self.app.query_var.set("")
        self.app.perform_search()
        text = self.app.results_text.get("1.0", tk.END)
        self.assertIn("Please enter a search query", text)

    def test_syntax_error_displayed_gracefully(self):
        """Verify syntax error is shown in the results area without crashing."""
        self.app.query_var.set("apple AND")
        self.app.perform_search()
        text = self.app.results_text.get("1.0", tk.END)
        self.assertIn("Query Syntax Error", text)


if __name__ == "__main__":
    unittest.main()


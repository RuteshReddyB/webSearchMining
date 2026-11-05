"""Module 7: GUI.

Tkinter front end for the search engine.
Adheres strictly to the design rule: the GUI only talks to SearchEngine.
Provides:
- ttk.Entry for queries
- ttk.Button for Search
- Read-only ScrolledText for results
- Enter key binding to trigger search
- Status bar and syntax hints
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional
from src.search_engine import SearchEngine
from src.query_processor import QueryError


class SearchApp:
    """Tkinter-based desktop interface for the Boolean Search Engine."""

    def __init__(self, root: tk.Tk, engine: SearchEngine) -> None:
        self.root = root
        self.engine = engine

        self.root.title("WSM Boolean Search Engine with Wildcards")
        self.root.geometry("820x620")
        self.root.minsize(650, 480)

        # Apply a modern clean ttk style
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self) -> None:
        """Create UI layout and widgets."""
        # Top Container Frame
        top_frame = ttk.Frame(self.root, padding=(14, 12, 14, 6))
        top_frame.pack(fill=tk.X)

        # Title Label
        title_label = ttk.Label(
            top_frame,
            text="Boolean Information Retrieval Engine",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 6))

        # Query Input Row
        input_frame = ttk.Frame(top_frame)
        input_frame.pack(fill=tk.X, pady=(2, 4))

        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(
            input_frame,
            textvariable=self.query_var,
            font=("Segoe UI", 11)
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=3)
        self.query_entry.focus_set()

        self.search_btn = ttk.Button(
            input_frame,
            text="Search",
            command=self.perform_search
        )
        self.search_btn.pack(side=tk.RIGHT, ipadx=10, ipady=3)

        # Enter key triggers search
        self.query_entry.bind("<Return>", lambda event: self.perform_search())

        # Syntax hint line
        syntax_hint = ttk.Label(
            top_frame,
            text="Syntax: AND  OR  NOT  ( )  * (multi-char wildcard)  ? (single-char wildcard)  [e.g. comp* AND NOT (network OR data)]",
            font=("Segoe UI", 8),
            foreground="#555555"
        )
        syntax_hint.pack(anchor=tk.W, pady=(2, 6))

        # Results Container Frame
        results_frame = ttk.Frame(self.root, padding=(14, 4, 14, 10))
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#fbfbfb",
            fg="#222222",
            padx=10,
            pady=10,
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Text tags for styling search results
        self.results_text.tag_config("header", font=("Consolas", 10, "bold"), foreground="#003366")
        self.results_text.tag_config("hit_title", font=("Consolas", 10, "bold"), foreground="#0b5394")
        self.results_text.tag_config("doc_id", foreground="#888888")
        self.results_text.tag_config("error", font=("Consolas", 10, "bold"), foreground="#c00000")
        self.results_text.tag_config("empty", font=("Consolas", 10, "italic"), foreground="#666666")

        # Initially read-only
        self.results_text.config(state=tk.DISABLED)

        # Status Bar
        self.status_var = tk.StringVar(
            value=f"Corpus: {self.engine.index.total_documents()} documents indexed | Vocabulary: {len(self.engine.index.vocabulary())} unique terms"
        )
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(10, 4),
            font=("Segoe UI", 8)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Show initial welcome text in result area
        self._set_result_content(
            "Welcome to the Boolean Search Engine!\n\n"
            "• Enter terms, Boolean operators (AND, OR, NOT), and wildcard patterns (*, ?).\n"
            "• Example queries:\n"
            "    1. computer AND science\n"
            "    2. comp* AND NOT network\n"
            "    3. (retrieval OR search) AND index*\n"
            "    4. *tion\n"
            "    5. d?ta\n\n"
            "Press Enter or click 'Search' to execute."
        )

    def _set_result_content(self, text: str, tag: Optional[str] = None) -> None:
        """Helper to safely write to the disabled ScrolledText."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        if tag:
            self.results_text.insert(tk.END, text, tag)
        else:
            self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)

    def perform_search(self) -> None:
        """Retrieve query, execute via engine, and format results."""
        query = self.query_var.get().strip()
        if not query:
            self._set_result_content("Please enter a search query.", "empty")
            self.status_var.set("Ready - Empty query provided.")
            return

        try:
            result = self.engine.search(query)
        except QueryError as qe:
            self._set_result_content(f"Query Syntax Error: {qe}\n\nPlease check your Boolean query format.", "error")
            self.status_var.set("Query error.")
            return
        except Exception as e:
            self._set_result_content(f"Unexpected error while searching: {e}", "error")
            self.status_var.set("Execution error.")
            return

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)

        num_hits = len(result.hits)
        header = f"{num_hits} document(s) found in {result.elapsed_ms:.2f} ms (out of {result.total_docs} documents)\n"
        self.results_text.insert(tk.END, header, "header")
        self.results_text.insert(tk.END, "=" * 70 + "\n\n")

        if num_hits == 0:
            self.results_text.insert(tk.END, "No documents matched the query criteria.\n", "empty")
        else:
            for rank, hit in enumerate(result.hits, start=1):
                doc_header = f"[{rank}] Document #{hit.doc_id}: {hit.filename}\n"
                self.results_text.insert(tk.END, doc_header, "hit_title")
                self.results_text.insert(tk.END, f"    Snippet: \"{hit.snippet}\"\n\n")

        self.results_text.config(state=tk.DISABLED)
        self.status_var.set(f"Completed in {result.elapsed_ms:.2f} ms | Found {num_hits} matching documents.")


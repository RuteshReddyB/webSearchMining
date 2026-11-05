"""Main entry point.

Initializes the SearchEngine facade with the corpus directory,
constructs the Tkinter root window, and launches the desktop GUI.
"""

import os
import sys
import tkinter as tk

# Ensure src can be imported when running directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.search_engine import SearchEngine
from src.gui import SearchApp


def main() -> None:
    corpus_dir = os.path.join(CURRENT_DIR, "data", "documents")

    print(f"Loading corpus and building inverted index from: {corpus_dir}")
    try:
        engine = SearchEngine(corpus_folder=corpus_dir)
        print(f"Index built successfully! {engine.index.total_documents()} documents, {len(engine.index.vocabulary())} vocabulary terms.")
    except Exception as e:
        print(f"Error initializing search engine: {e}", file=sys.stderr)
        sys.exit(1)

    root = tk.Tk()
    app = SearchApp(root, engine)
    root.mainloop()


if __name__ == "__main__":
    main()


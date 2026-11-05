# Boolean Search Engine with Wildcard Support

A modular Information Retrieval (IR) search engine written in Python 3 with a Tkinter graphical user interface (GUI). It implements an inverted index, Boolean retrieval models (`AND`, `OR`, `NOT`, and nested parentheses), and arbitrary wildcard search (`*` and `?`) using a k-gram (bigram) index with post-filtering.

---

## 1. Project Structure

```
webSearchMining/
├── main.py                  # Entry point: builds engine, launches GUI
├── data/
│   └── documents/           # Corpus (.txt files)
├── src/
│   ├── __init__.py
│   ├── document_loader.py   # Module 1: Corpus reading & document ID assignment
│   ├── tokenizer.py         # Module 2: Text tokenization
│   ├── normalizer.py        # Module 3: Unicode case-folding & normalization
│   ├── inverted_index.py    # Module 4: Inverted index & postings lists
│   ├── query_processor.py   # Module 5: Shunting-yard parsing & Boolean evaluation
│   ├── wildcard.py          # Module 6: K-gram (bigram) index & regex post-filtering
│   ├── search_engine.py     # Facade tying all modules together
│   └── gui.py               # Module 7: Tkinter desktop GUI
├── tests/
│   ├── test_tokenizer.py
│   ├── test_normalizer.py
│   ├── test_index.py
│   ├── test_query.py
│   └── test_wildcard.py
└── README.md
```

---

## 2. Architecture & Data Flow

### Indexing Pipeline (Startup)
```
Loader (data/documents) 
   ↓
Tokenizer (regex [A-Za-z0-9]+(?:'[A-Za-z]+)?)
   ↓
Normalizer (Unicode case-folding str.casefold())
   ↓
InvertedIndex.add() (postings & positional lists)
   ↓
WildcardIndex.build() (bigram inverted index over vocabulary)
```

### Searching Pipeline (Per Query)
```
GUI (Input Query)
   ↓
SearchEngine.search(q)
   ↓
QueryProcessor.tokenize_query() (lexer splitting terms, operators, parens)
   ↓
QueryProcessor.infix_to_postfix() (Shunting-yard algorithm with implicit AND)
   ↓
QueryProcessor.evaluate_postfix() (Stack evaluation)
   ├── Exact terms: InvertedIndex.get_postings()
   ├── Wildcard terms: WildcardIndex.expand() → Union of matching postings
   ├── AND: Two-pointer sorted list intersection (shortest first)
   ├── OR: Two-pointer sorted list union
   └── NOT: Set difference against Universe of all Doc IDs
   ↓
Result doc IDs → Snippet generation → GUI Display
```

---

## 3. Design Choices & Documented Rules

### Tokenization (`src/tokenizer.py`)
- Regex pattern: `[A-Za-z0-9]+(?:'[A-Za-z]+)?`
- **Contractions:** Preserved as single tokens (e.g. `don't`, `user's`).
- **Hyphens & Punctuation:** Treated as word delimiters (e.g. `state-of-the-art` produces `state`, `of`, `the`, `art`).
- **Case:** Tokenizer preserves raw case. Case-folding is exclusively performed by the normalizer.

### Normalization (`src/normalizer.py`)
- Uses Python's `str.casefold()` rather than `lower()`, ensuring correct handling of international characters (e.g. German `"STRASSE"` and `"Straße"` both map to `"strasse"`).
- **Wildcard Safety:** Wildcard characters (`*` and `?`) are explicitly preserved during query term normalization.
- Optional stop-word removal is supported via configurable flag.

### Inverted Index (`src/inverted_index.py`)
- Maps normalized terms to sorted lists of document IDs.
- Tracks positions for optional phrase queries.
- Maintains the total universe of document IDs required for the unary `NOT` operator.
- Supports serialization to JSON or Pickle.

### Query Processor (`src/query_processor.py`)
- **Operator Precedence:** `NOT` (precedence 3, right-associative) > `AND` (precedence 2, left-associative) > `OR` (precedence 1, left-associative).
- **Implicit AND:** Adjacent terms (e.g., `computer science` or `(apple OR banana) fruit`) automatically receive an implicit `AND`.
- **Set Operations:** Evaluated using efficient two-pointer linear scans over sorted posting lists (`O(m + n)`).

### Wildcard Expansion (`src/wildcard.py`): K-Gram vs. Permuterm
- **Approach chosen: K-Gram (Bigram) Index with Regex Post-Filtering.**
- **Justification:**
  - Unlike a permuterm index which expands rotational prefixes for a single wildcard `*`, a k-gram index handles arbitrary wildcard patterns:
    - Prefix: `comp*`
    - Suffix: `*tion`
    - Middle: `c*t`, `h?llo`
    - Multiple wildcards: `c*m*n`, `*a*b*`
  - Term padding with `$` anchors the boundaries (`$cat$`).
  - Constant substrings produce bigrams (`$c`, `at`, etc.) whose term sets are intersected.
  - Regex post-filtering eliminates false positives introduced by k-gram collisions.

---

## 4. Query Syntax & Examples

| Query Pattern | Description | Example Query |
| :--- | :--- | :--- |
| **Single Term** | Case-insensitive single word | `computer` |
| **Boolean AND** | Documents containing both terms | `computer AND science` |
| **Boolean OR** | Documents containing either term | `retrieval OR search` |
| **Boolean NOT** | Documents not containing the term | `NOT network` |
| **Compound Boolean** | Precedence `NOT` > `AND` > `OR` | `computer AND NOT network` |
| **Grouping** | Parentheses override precedence | `(retrieval OR search) AND index*` |
| **Implicit AND** | Adjacent terms without operators | `data structures` |
| **Prefix Wildcard** | Starts with prefix | `comp*` |
| **Suffix Wildcard** | Ends with suffix | `*tion` |
| **Single-Char Wildcard**| `?` matches exactly 1 character | `h?llo`, `d?ta` |
| **Complex Wildcard** | Multiple `*` and `?` | `c*m*n` |

---

## 5. How to Run

### Requirements
- Python 3.8+ (standard library only; uses built-in `tkinter`, `unittest`, `re`, `json`, `pickle`).

### Launch the GUI
```bash
python main.py
```

### Run Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
Ran 32 unit tests covering all modules with 100% pass rate.

"""Module 5: Query Processor.

Responsible for:
1. Tokenizing user queries into terms, Boolean operators (AND, OR, NOT), and parentheses.
2. Converting infix notation to postfix using Dijkstra's Shunting-Yard algorithm.
3. Supporting implicit AND between adjacent terms.
4. Evaluating postfix expression using stack operations with two-pointer list intersections.
5. Delegating wildcard terms (* and ?) to WildcardIndex and taking postings union.
"""

import re
from typing import Callable, List, Optional, Set
from src.normalizer import normalize_term


class QueryError(Exception):
    """Raised when a query has invalid syntax or cannot be evaluated."""
    pass


class QueryProcessor:
    """Parses and evaluates Boolean queries with wildcard support."""

    # Operator precedence and associativity
    PRECEDENCE = {
        "NOT": 3,
        "AND": 2,
        "OR": 1,
    }

    def __init__(
        self,
        get_postings_fn: Callable[[str], List[int]],
        all_doc_ids_fn: Callable[[], List[int]],
        expand_wildcard_fn: Optional[Callable[[str], List[str]]] = None,
    ) -> None:
        """Initialize QueryProcessor with index lookup callbacks."""
        self.get_postings = get_postings_fn
        self.all_doc_ids = all_doc_ids_fn
        self.expand_wildcard = expand_wildcard_fn

    @staticmethod
    def tokenize_query(query: str) -> List[str]:
        """Tokenize query string into operators, parentheses, and terms."""
        if not query or not query.strip():
            return []

        # Regex capturing parentheses, or non-whitespace sequences
        # e.g. "comp* AND NOT (network OR data)" -> ['comp*', 'AND', 'NOT', '(', 'network', 'OR', 'data', ')']
        pattern = re.compile(r"\(|\)|[^\s\(\)]+")
        raw_tokens = pattern.findall(query.strip())
        return raw_tokens

    def _insert_implicit_and(self, tokens: List[str]) -> List[str]:
        """Insert implicit AND operators between adjacent terms or parenthesized groups.

        Example:
            ["apple", "banana"] -> ["apple", "AND", "banana"]
            [")", "cat"] -> [")", "AND", "cat"]
            ["cat", "("] -> ["cat", "AND", "("]
            [")", "("] -> [")", "AND", "("]
        """
        output: List[str] = []
        for i, token in enumerate(tokens):
            if i > 0:
                prev = tokens[i - 1]
                # Can prev be followed by an implicit AND?
                # prev can be a term, or ')'
                prev_is_operand = prev not in {"AND", "OR", "NOT", "("}
                # Can current be preceded by an implicit AND?
                # current can be a term, '(', or 'NOT'
                curr_is_operand_or_start = token not in {"AND", "OR", ")"}

                if prev_is_operand and curr_is_operand_or_start:
                    output.append("AND")

            output.append(token)
        return output

    def infix_to_postfix(self, tokens: List[str]) -> List[str]:
        """Convert infix token list to postfix (Reverse Polish Notation) using Shunting-Yard."""
        tokens_with_and = self._insert_implicit_and(tokens)
        output: List[str] = []
        operator_stack: List[str] = []

        for token in tokens_with_and:
            if token in {"AND", "OR"}:
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and (
                        self.PRECEDENCE.get(operator_stack[-1], 0) > self.PRECEDENCE[token]
                        or (
                            self.PRECEDENCE.get(operator_stack[-1], 0) == self.PRECEDENCE[token]
                            # Left-associative for AND / OR
                        )
                    )
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(token)

            elif token == "NOT":
                # NOT is unary and right-associative (precedence 3)
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and self.PRECEDENCE.get(operator_stack[-1], 0) > self.PRECEDENCE["NOT"]
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(token)

            elif token == "(":
                operator_stack.append(token)

            elif token == ")":
                matched = False
                while operator_stack:
                    top = operator_stack.pop()
                    if top == "(":
                        matched = True
                        break
                    output.append(top)
                if not matched:
                    raise QueryError("Mismatched parentheses: unexpected closing ')'")

            else:
                # Ordinary term / wildcard term
                output.append(token)

        while operator_stack:
            top = operator_stack.pop()
            if top in {"(", ")"}:
                raise QueryError("Mismatched parentheses: unclosed '(' in query")
            output.append(top)

        return output

    # --- Set operations on sorted postings lists ---

    @staticmethod
    def _intersect(p1: List[int], p2: List[int]) -> List[int]:
        """Two-pointer intersection of two sorted doc ID lists."""
        result: List[int] = []
        i, j = 0, 0
        len1, len2 = len(p1), len(p2)
        while i < len1 and j < len2:
            d1, d2 = p1[i], p2[j]
            if d1 == d2:
                result.append(d1)
                i += 1
                j += 1
            elif d1 < d2:
                i += 1
            else:
                j += 1
        return result

    @staticmethod
    def _union(p1: List[int], p2: List[int]) -> List[int]:
        """Two-pointer union of two sorted doc ID lists."""
        result: List[int] = []
        i, j = 0, 0
        len1, len2 = len(p1), len(p2)
        while i < len1 and j < len2:
            d1, d2 = p1[i], p2[j]
            if d1 == d2:
                result.append(d1)
                i += 1
                j += 1
            elif d1 < d2:
                result.append(d1)
                i += 1
            else:
                result.append(d2)
                j += 1
        while i < len1:
            result.append(p1[i])
            i += 1
        while j < len2:
            result.append(p2[j])
            j += 1
        return result

    @staticmethod
    def _difference(universe: List[int], postings: List[int]) -> List[int]:
        """Difference: universe \ postings (for NOT operation)."""
        result: List[int] = []
        i, j = 0, 0
        u_len, p_len = len(universe), len(postings)
        while i < u_len and j < p_len:
            u_doc = universe[i]
            p_doc = postings[j]
            if u_doc == p_doc:
                i += 1
                j += 1
            elif u_doc < p_doc:
                result.append(u_doc)
                i += 1
            else:
                j += 1
        while i < u_len:
            result.append(universe[i])
            i += 1
        return result

    def _resolve_term(self, raw_term: str) -> List[int]:
        """Resolve a single term or wildcard pattern to a postings list."""
        norm = normalize_term(raw_term)
        if not norm:
            return []

        # Check if wildcard
        if "*" in norm or "?" in norm:
            if not self.expand_wildcard:
                raise QueryError("Wildcard expansion is not configured.")
            expanded_terms = self.expand_wildcard(norm)
            if not expanded_terms:
                return []
            # Take union of postings for all expanded terms
            postings_sets: Set[int] = set()
            for t in expanded_terms:
                postings_sets.update(self.get_postings(t))
            return sorted(postings_sets)

        # Standard term
        return self.get_postings(norm)

    def evaluate_postfix(self, postfix_tokens: List[str]) -> List[int]:
        """Evaluate postfix token stream using an evaluation stack."""
        if not postfix_tokens:
            return []

        stack: List[List[int]] = []
        universe = self.all_doc_ids()

        for token in postfix_tokens:
            if token == "NOT":
                if not stack:
                    raise QueryError("Dangling NOT operator: missing operand")
                operand = stack.pop()
                stack.append(self._difference(universe, operand))

            elif token in {"AND", "OR"}:
                if len(stack) < 2:
                    raise QueryError(f"Dangling binary operator '{token}': insufficient operands")
                right = stack.pop()
                left = stack.pop()
                if token == "AND":
                    # Optimization: run shortest list first
                    if len(left) <= len(right):
                        stack.append(self._intersect(left, right))
                    else:
                        stack.append(self._intersect(right, left))
                else:  # OR
                    stack.append(self._union(left, right))

            else:
                # Term or wildcard pattern
                postings = self._resolve_term(token)
                stack.append(postings)

        if len(stack) != 1:
            raise QueryError("Invalid query: multiple disconnected terms or operators")

        return stack[0]

    def execute(self, query_str: str) -> List[int]:
        """Parse and evaluate a full query string."""
        raw_tokens = self.tokenize_query(query_str)
        if not raw_tokens:
            return []

        postfix = self.infix_to_postfix(raw_tokens)
        return self.evaluate_postfix(postfix)


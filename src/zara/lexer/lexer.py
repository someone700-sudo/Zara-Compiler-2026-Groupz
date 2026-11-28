"""
Lexical analyser (scanner) for the Zara language (Week 2).

WHY regex-based: The assignment requires a regex-based lexer.  We use
compiled regex patterns from the ``re`` module to match each token category.
A manual scan loop walks the source character-by-character, trying the
master regex at each position.  Multi-line comments are handled separately
because they can span newlines that the master regex (without DOTALL) would
miss, and because we need to report *unterminated* comments cleanly.

Error detection:
  - Illegal characters (characters outside the Zara alphabet)
  - Unterminated string literals (missing closing ")
  - Unterminated multi-line comments (missing closing */)
  - Malformed tokens trigger skip-and-continue recovery so the lexer
    reports all errors in one pass rather than stopping at the first.
"""

import re
from typing import List

from zara.errors.error_handler import ErrorHandler, ErrorPhase
from zara.lexer.tokens import Token, TokenType, KEYWORDS

# ---------------------------------------------------------------------------
# Regex patterns for each token category.
# ORDER MATTERS: longer matches must come before shorter prefixes
# (e.g. '==' before '=').  Float must come before Int so "3.14" matches
# as one FLOAT_LIT rather than INT "3", DOT, INT "14".
# ---------------------------------------------------------------------------

_TOKEN_SPEC: List[tuple] = [
    ("SL_COMMENT",  r"//[^\n]*"),              # single-line comment (skip)
    ("NEWLINE",     r"\n"),                     # newline (track line no.)
    ("WHITESPACE",  r"[ \t\r]+"),              # whitespace (skip)
    ("FLOAT_LIT",   r"\d+\.\d+"),              # e.g. 3.14
    ("INT_LIT",     r"\d+"),                    # e.g. 42
    ("STRING_LIT",  r'"[^"\n]*"'),             # complete string
    ("UNTERM_STR",  r'"[^"\n]*'),              # unterminated string (error)
    ("EQ_EQ",       r"=="),                     # equality
    ("ASSIGN",      r"="),                      # assignment
    ("STAR",        r"\*"),                     # multiplication
    # SLASH is handled manually (it could start a comment) —
    # but since we already stripped comments above, a bare '/' here is division.
    ("SLASH",       r"/"),                      # division
    ("MINUS",       r"-"),                      # subtraction
    ("GT",          r">"),                      # greater-than / generic close
    ("LT",          r"<"),                      # generic type open only
    ("LPAREN",      r"\("),
    ("RPAREN",      r"\)"),
    ("LBRACE",      r"\{"),
    ("RBRACE",      r"\}"),
    ("LBRACKET",    r"\["),
    ("RBRACKET",    r"\]"),
    ("SEMICOLON",   r";"),
    ("COMMA",       r","),
    ("DOT",         r"\."),
    ("IDENT",       r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("MISMATCH",    r"."),                      # any other single char (error)
]

# Map regex group names to TokenType values for operators / delimiters.
_GROUP_TO_TYPE: dict = {
    "EQ_EQ":     TokenType.EQ_EQ,
    "ASSIGN":    TokenType.ASSIGN,
    "STAR":      TokenType.STAR,
    "SLASH":     TokenType.SLASH,
    "MINUS":     TokenType.MINUS,
    "GT":        TokenType.GT,
    "LT":        TokenType.LT,
    "LPAREN":    TokenType.LPAREN,
    "RPAREN":    TokenType.RPAREN,
    "LBRACE":    TokenType.LBRACE,
    "RBRACE":    TokenType.RBRACE,
    "LBRACKET":  TokenType.LBRACKET,
    "RBRACKET":  TokenType.RBRACKET,
    "SEMICOLON": TokenType.SEMICOLON,
    "COMMA":     TokenType.COMMA,
    "DOT":       TokenType.DOT,
}

_MASTER_PATTERN = "|".join(
    f"(?P<{name}>{pattern})" for name, pattern in _TOKEN_SPEC
)
_MASTER_RE = re.compile(_MASTER_PATTERN)


class Lexer:
    """
    Regex-based lexical analyser for Zara source code.

    Usage::

        handler = ErrorHandler()
        lexer   = Lexer(handler)
        tokens  = lexer.tokenize(source_code)
    """

    def __init__(self, error_handler: ErrorHandler):
        self.errors = error_handler

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def tokenize(self, source: str) -> List[Token]:
        """
        Scan *source* and return a list of Token objects, ending with EOF.
        Lexical errors are reported through the ErrorHandler; the lexer
        recovers by skipping the offending character and continuing.
        """
        tokens: List[Token] = []
        pos = 0
        line = 1
        line_start = 0          # byte offset of the current line's start

        while pos < len(source):
            # --- Multi-line comments: handled before the master regex ---
            if source[pos:pos + 2] == "/*":
                col = pos - line_start + 1
                end = source.find("*/", pos + 2)
                if end == -1:
                    self.errors.report(
                        ErrorPhase.LEXER, line, col,
                        "Unterminated multi-line comment",
                        "Add '*/' to close the comment")
                    break              # rest of file consumed as comment
                # Count newlines inside the comment to keep line tracking
                comment = source[pos:end + 2]
                nl_count = comment.count("\n")
                line += nl_count
                if nl_count > 0:
                    # line_start = position after the last newline in comment
                    last_nl = comment.rfind("\n")
                    line_start = pos + last_nl + 1
                pos = end + 2
                continue

            # --- Master regex match at current position ---
            m = _MASTER_RE.match(source, pos)
            if m is None:
                break                  # safety: should never happen

            kind = m.lastgroup
            value = m.group()
            col = pos - line_start + 1

            if kind == "NEWLINE":
                line += 1
                line_start = m.end()

            elif kind == "WHITESPACE" or kind == "SL_COMMENT":
                pos = m.end()
                continue

            elif kind == "FLOAT_LIT":
                tokens.append(Token(TokenType.FLOAT_LIT, value, line, col))

            elif kind == "INT_LIT":
                tokens.append(Token(TokenType.INT_LIT, value, line, col))

            elif kind == "STRING_LIT":
                tokens.append(Token(TokenType.STRING_LIT, value, line, col))

            elif kind == "UNTERM_STR":
                self.errors.report(
                    ErrorPhase.LEXER, line, col,
                    "Unterminated string literal",
                    "Add a closing '\"' to the string")
                # Recover: treat as a string with an implicit close
                tokens.append(
                    Token(TokenType.STRING_LIT, value + '"', line, col))

            elif kind == "IDENT":
                tt = KEYWORDS.get(value, TokenType.IDENT)
                tokens.append(Token(tt, value, line, col))

            elif kind == "MISMATCH":
                self.errors.report(
                    ErrorPhase.LEXER, line, col,
                    f"Illegal character: {value!r}",
                    "Remove this character")
                # Recovery: skip the character (token not emitted)

            else:
                # Operator or delimiter — look up the token type
                tt = _GROUP_TO_TYPE.get(kind)
                if tt is not None:
                    tokens.append(Token(tt, value, line, col))

            pos = m.end()

        # Always end the token stream with EOF
        tokens.append(
            Token(TokenType.EOF, "", line, pos - line_start + 1))
        return tokens

    # ------------------------------------------------------------------ #
    #  Display helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def format_tokens(tokens: List[Token]) -> str:
        """Format a token list as a table for the --tokens flag."""
        sep = "-" * 60
        lines = [
            "",
            sep,
            f"  {'TOKEN TYPE':<18} {'VALUE':<22} {'LOCATION'}",
            sep,
        ]
        for tok in tokens:
            if tok.type == TokenType.EOF:
                lines.append(f"  {'EOF':<18} {'':22} Line {tok.line}, Col {tok.col}")
                break
            lines.append(
                f"  {tok.type.name:<18} {tok.value!r:<22} "
                f"Line {tok.line}, Col {tok.col}")
        lines.append(sep)
        return "\n".join(lines)

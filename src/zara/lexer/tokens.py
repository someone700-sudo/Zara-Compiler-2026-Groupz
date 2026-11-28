"""
Token types and Token class for the Zara lexer.

WHY: Every token the lexer produces carries a type, the original text (value),
and the source location (line, column). The TokenType enum lists every distinct
token the language recognises — the six operators, keywords, literals,
delimiters, and two special markers (EOF, ERROR).
"""

from enum import Enum, auto


class TokenType(Enum):
    """Every distinct token category in the Zara language."""

    # ---- Literals ----
    INT_LIT = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()

    # ---- Identifier ----
    IDENT = auto()

    # ---- Type keywords ----
    KW_INTEGER = auto()
    KW_FLOAT = auto()
    KW_STRING = auto()
    KW_ARRAY = auto()
    KW_STACK = auto()

    # ---- Control-flow keywords ----
    KW_IF = auto()
    KW_ELSE = auto()
    KW_DO = auto()
    KW_WHILE = auto()
    KW_FOR = auto()

    # ---- Subprogram keywords ----
    KW_FUNCTION = auto()
    KW_RETURN = auto()

    # ---- OOP keywords ----
    KW_CLASS = auto()
    KW_EXTENDS = auto()
    KW_NEW = auto()
    KW_THIS = auto()

    # ---- Built-in I/O ----
    KW_PRINT = auto()

    # ---- Operators (exactly 6 — no others are permitted) ----
    ASSIGN = auto()       # =
    STAR = auto()         # *
    SLASH = auto()        # /
    MINUS = auto()        # -
    GT = auto()           # >
    EQ_EQ = auto()        # ==

    # ---- Delimiters / punctuation ----
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    SEMICOLON = auto()    # ;
    COMMA = auto()        # ,
    DOT = auto()          # .
    LT = auto()           # < (used only in generic type syntax: Array<T>)

    # ---- Special ----
    EOF = auto()
    ERROR = auto()


# Map keyword strings to their token types.
KEYWORDS: dict = {
    "Integer":  TokenType.KW_INTEGER,
    "Float":    TokenType.KW_FLOAT,
    "String":   TokenType.KW_STRING,
    "Array":    TokenType.KW_ARRAY,
    "Stack":    TokenType.KW_STACK,
    "if":       TokenType.KW_IF,
    "else":     TokenType.KW_ELSE,
    "do":       TokenType.KW_DO,
    "while":    TokenType.KW_WHILE,
    "for":      TokenType.KW_FOR,
    "function": TokenType.KW_FUNCTION,
    "return":   TokenType.KW_RETURN,
    "class":    TokenType.KW_CLASS,
    "extends":  TokenType.KW_EXTENDS,
    "new":      TokenType.KW_NEW,
    "this":     TokenType.KW_THIS,
    "print":    TokenType.KW_PRINT,
}


class Token:
    """
    A single lexical token.
    Carries its type, the matched source text, and its position (line, col)
    so that later phases can produce accurate error messages.
    """

    __slots__ = ("type", "value", "line", "col")

    def __init__(self, token_type: TokenType, value: str,
                 line: int, col: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        return (f"Token({self.type.name}, {self.value!r}, "
                f"L{self.line}:C{self.col})")

    def __str__(self) -> str:
        return (f"{self.type.name:15s} | {self.value!r:20s} | "
                f"Line {self.line}, Col {self.col}")

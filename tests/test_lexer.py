"""
Unit tests for the Zara Lexical Analyzer (Week 2).
"""

import unittest
from zara.lexer.lexer import Lexer
from zara.lexer.tokens import TokenType
from zara.errors.error_handler import ErrorHandler, ErrorPhase


class TestLexer(unittest.TestCase):

    def setUp(self):
        self.errors = ErrorHandler()
        self.lexer = Lexer(self.errors)

    def test_keywords_and_types(self):
        source = "Integer Float String Array Stack if else do while for function return class extends new this print"
        tokens = self.lexer.tokenize(source)
        expected_types = [
            TokenType.KW_INTEGER, TokenType.KW_FLOAT, TokenType.KW_STRING,
            TokenType.KW_ARRAY, TokenType.KW_STACK, TokenType.KW_IF,
            TokenType.KW_ELSE, TokenType.KW_DO, TokenType.KW_WHILE,
            TokenType.KW_FOR, TokenType.KW_FUNCTION, TokenType.KW_RETURN,
            TokenType.KW_CLASS, TokenType.KW_EXTENDS, TokenType.KW_NEW,
            TokenType.KW_THIS, TokenType.KW_PRINT, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
        self.assertFalse(self.errors.has_errors())

    def test_the_six_operators_only(self):
        source = "= * / - > =="
        tokens = self.lexer.tokenize(source)
        expected = [
            TokenType.ASSIGN, TokenType.STAR, TokenType.SLASH,
            TokenType.MINUS, TokenType.GT, TokenType.EQ_EQ, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], expected)

    def test_literals(self):
        source = '42 3.14 "hello world"'
        tokens = self.lexer.tokenize(source)
        self.assertEqual(tokens[0].type, TokenType.INT_LIT)
        self.assertEqual(tokens[0].value, "42")
        self.assertEqual(tokens[1].type, TokenType.FLOAT_LIT)
        self.assertEqual(tokens[1].value, "3.14")
        self.assertEqual(tokens[2].type, TokenType.STRING_LIT)
        self.assertEqual(tokens[2].value, '"hello world"')

    def test_comments_stripped(self):
        source = """
        // This is single line
        Integer x = 5; /* This is
        multiline */
        Float y = 2.5;
        """
        tokens = self.lexer.tokenize(source)
        # Comments should be absent
        types = [t.type for t in tokens]
        self.assertNotIn(TokenType.ERROR, types)
        self.assertEqual(types[0], TokenType.KW_INTEGER)
        self.assertEqual(types[1], TokenType.IDENT)
        self.assertEqual(types[2], TokenType.ASSIGN)
        self.assertEqual(types[3], TokenType.INT_LIT)
        self.assertEqual(types[4], TokenType.SEMICOLON)

    def test_lexical_error_detection_and_recovery(self):
        # Character '@' and '&' are not in Zara alphabet
        source = 'Integer x = 5 @ 3 & "unterminated;'
        tokens = self.lexer.tokenize(source)
        self.assertTrue(self.errors.has_errors())
        lex_errors = self.errors.get_errors(ErrorPhase.LEXER)
        self.assertGreaterEqual(len(lex_errors), 2)  # '@' and '&' and unterminated string
        # Confirm recovery: lexer completed and returned EOF
        self.assertEqual(tokens[-1].type, TokenType.EOF)


if __name__ == "__main__":
    unittest.main()

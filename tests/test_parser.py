"""
Unit tests for the Recursive Descent Parser (Week 3).
"""

import unittest
from zara.lexer.lexer import Lexer
from zara.parser.recursive_descent import RecursiveDescentParser
from zara.errors.error_handler import ErrorHandler, ErrorPhase
from zara.ast.nodes import (
    Program, VarDecl, FunctionDecl, ClassDecl, IfStmt, ForStmt,
    DoWhileStmt, PrintStmt, BinaryOp
)


class TestRecursiveDescentParser(unittest.TestCase):

    def parse_source(self, source: str):
        handler = ErrorHandler()
        lexer = Lexer(handler)
        tokens = lexer.tokenize(source)
        parser = RecursiveDescentParser(tokens, handler)
        ast = parser.parse()
        return ast, handler

    def test_variable_declarations(self):
        source = """
        Integer x = 10;
        Float y = 3.14;
        String s = "hello";
        Array<Integer> arr = [1, 2, 3];
        Stack<Integer> st = new Stack();
        """
        ast, handler = self.parse_source(source)
        self.assertFalse(handler.has_errors())
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.declarations), 5)
        for decl in ast.declarations:
            self.assertIsInstance(decl, VarDecl)

    def test_operator_precedence(self):
        # x = 10 - 2 * 3;
        # Multiplicative (2 * 3) must be under subtraction (-)
        source = "Integer x = 10 - 2 * 3;"
        ast, handler = self.parse_source(source)
        self.assertFalse(handler.has_errors())
        vdecl = ast.declarations[0]
        expr = vdecl.initializer
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "-")
        self.assertEqual(expr.left.value, 10)
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "*")

    def test_control_structures(self):
        source = """
        if (x > 0) {
            print(x);
        } else {
            print(0);
        }

        for (Integer i = 10; i > 0; i = i - 1) {
            print(i);
        }

        do {
            x = x - 1;
        } while (x > 0);
        """
        ast, handler = self.parse_source(source)
        self.assertFalse(handler.has_errors())
        self.assertEqual(len(ast.declarations), 3)
        self.assertIsInstance(ast.declarations[0], IfStmt)
        self.assertIsInstance(ast.declarations[1], ForStmt)
        self.assertIsInstance(ast.declarations[2], DoWhileStmt)

    def test_functions_and_classes(self):
        source = """
        function Integer mul(Integer a, Integer b) {
            return a * b;
        }

        class Animal {
            Integer age;
            Integer speak() {
                return 0;
            }
        }

        class Dog extends Animal {
            Integer speak() {
                return 1;
            }
        }
        """
        ast, handler = self.parse_source(source)
        self.assertFalse(handler.has_errors())
        self.assertEqual(len(ast.declarations), 3)
        self.assertIsInstance(ast.declarations[0], FunctionDecl)
        self.assertIsInstance(ast.declarations[1], ClassDecl)
        self.assertIsInstance(ast.declarations[2], ClassDecl)
        self.assertEqual(ast.declarations[2].parent_name, "Animal")

    def test_syntax_error_recovery(self):
        # Missing semicolon in first stmt, second stmt should still parse
        source = """
        Integer x = 10
        Integer y = 20;
        """
        ast, handler = self.parse_source(source)
        self.assertTrue(handler.has_errors())
        # Parser should have synchronized and parsed 'Integer y = 20;'
        var_names = [d.name for d in ast.declarations if isinstance(d, VarDecl)]
        self.assertIn("y", var_names)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for the Zara Symbol Table (Week 1).
"""

import unittest
from zara.symboltable.symbol_table import SymbolTable, SymbolInfo


class TestSymbolTable(unittest.TestCase):

    def setUp(self):
        self.st = SymbolTable()

    def test_add_and_lookup_basic(self):
        sym = SymbolInfo("x", "variable", "Integer", line=1, col=1)
        self.assertTrue(self.st.add("x", sym))
        found = self.st.lookup("x")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "x")
        self.assertEqual(found.data_type, "Integer")
        self.assertEqual(found.scope_level, 0)

    def test_duplicate_in_same_scope(self):
        sym1 = SymbolInfo("x", "variable", "Integer", line=1, col=1)
        sym2 = SymbolInfo("x", "variable", "Float", line=2, col=1)
        self.assertTrue(self.st.add("x", sym1))
        self.assertFalse(self.st.add("x", sym2))  # duplicate in scope 0
        found = self.st.lookup("x")
        self.assertEqual(found.data_type, "Integer")

    def test_nested_scope_shadowing(self):
        # Global x = Integer
        self.st.add("x", SymbolInfo("x", "variable", "Integer", line=1, col=1))
        self.st.enter_scope()

        # Inner x = Float (shadowing allowed)
        self.assertTrue(self.st.add("x", SymbolInfo("x", "variable", "Float", line=5, col=5)))
        found_inner = self.st.lookup("x")
        self.assertEqual(found_inner.data_type, "Float")
        self.assertEqual(found_inner.scope_level, 1)

        self.st.exit_scope()
        found_outer = self.st.lookup("x")
        self.assertEqual(found_outer.data_type, "Integer")
        self.assertEqual(found_outer.scope_level, 0)

    def test_search_and_retrieve(self):
        sym = SymbolInfo("nums", "variable", "Array<Integer>", element_type="Integer", size=10)
        self.st.add("nums", sym)
        self.assertTrue(self.st.search("nums"))
        self.assertFalse(self.st.search("missing_var"))
        retrieved = self.st.retrieve("nums")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.element_type, "Integer")
        self.assertEqual(retrieved.size, 10)

    def test_update_symbol(self):
        sym = SymbolInfo("count", "variable", "Integer")
        self.st.add("count", sym)
        updated = SymbolInfo("count", "variable", "Integer", size=42)
        self.assertTrue(self.st.update("count", updated))
        self.assertEqual(self.st.lookup("count").size, 42)
        self.assertFalse(self.st.update("non_existent", sym))

    def test_all_five_types_support(self):
        # Integer, Float, String, Array, Stack
        self.assertTrue(self.st.add("a", SymbolInfo("a", "variable", "Integer")))
        self.assertTrue(self.st.add("b", SymbolInfo("b", "variable", "Float")))
        self.assertTrue(self.st.add("c", SymbolInfo("c", "variable", "String")))
        self.assertTrue(self.st.add("d", SymbolInfo("d", "variable", "Array<Float>", element_type="Float")))
        self.assertTrue(self.st.add("e", SymbolInfo("e", "variable", "Stack<Integer>", element_type="Integer")))

        for name in ["a", "b", "c", "d", "e"]:
            self.assertTrue(self.st.search(name))


if __name__ == "__main__":
    unittest.main()

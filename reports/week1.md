# Week 1 Progress Report: Overview of Compilers and Symbol Table

## 1. What Was Built
- Implemented a scoped Symbol Table in `src/zara/symboltable/symbol_table.py`.
- Supports all five Zara data types: `Integer`, `Float`, `String`, `Array`, and `Stack`, as well as user-defined class types.
- Operations implemented: `add` (with duplicate detection in the active scope), `update`, `search`, and `retrieve` (lookup).
- Full tracking of name, data type, scope level, source coordinates (line, column), element type/size for `Array` and `Stack`, and subprogram details (return type, parameter list).
- Nested lexical scoping support via a stack of scope dictionaries (`enter_scope`, `exit_scope`).
- Standalone demonstration routine `demo_symbol_table()` executable via CLI (`--demo-symbols`).

## 2. Design Choices
- **Scope Stack Structure:** Managed as a Python `list[dict[str, SymbolInfo]]`. Global scope is index 0. Scopes push on entry and pop on exit. Lookups traverse reversed list to achieve lexical scoping and variable shadowing.
- **SymbolInfo Dataclass:** Unifies variable symbols, array/stack type metadata, function signatures, and class hierarchies within a clean, extensible structure.

## 3. Test Results
- Suite: `tests/test_symbol_table.py`
- Executed 6 unit tests covering basic insertion/lookup, duplicate detection within the same scope, nested scope shadowing, search and retrieve, symbol updating, and coverage of all five Zara types.
- All 6 tests passed without errors.

## 4. Limitations
- At Week 1, the symbol table was populated programmatically via test cases and the demo script. From Week 3 and 5 onward, it is populated automatically by the parser and semantic analyzer.

## 5. How to Explain This (Viva Preparation)

### Talking Points
1. The symbol table is the central compile-time database recording every identifier's name, type, and location.
2. We implemented a scoped symbol table using a stack of hash tables (dictionaries), where each stack frame represents a lexical block.
3. Name lookup follows static lexical scoping: searching starts at the top of the stack (innermost block) and proceeds downward to global scope.
4. Variable shadowing is naturally supported: an inner declaration masks an outer declaration without overwriting it.
5. Duplicate identifiers in the same scope are prohibited and caught during insertion.
6. Generic collections (`Array<T>` and `Stack<T>`) store both base container type and inner element type metadata.
7. Subprograms record parameter signatures and return types to enable compile-time arity and type checking.

### Key Algorithm: Lexical Scope Lookup
```
Algorithm Lookup(name):
  Input: Identifier string name
  Output: SymbolInfo if found, else None

  1. For each scope dictionary in reverse order (from innermost to outermost):
       If name exists in scope:
           Return scope[name]
  2. Return None (symbol is undeclared in accessible scopes)
```

### Likely Examiner Questions & Model Answers
**Q1: Why use a stack of tables instead of a single global table with scope tags?**  
*Answer:* A stack of dictionaries makes block entry and exit an O(1) push and pop operation. When a block ends, popping the innermost scope instantly invalidates all local variables declared within it, preventing memory leaks and avoiding complex cleanup sweeps.

**Q2: How does your symbol table handle variable shadowing?**  
*Answer:* Because lookup traverses the scope stack in reverse (from current innermost scope towards global scope), the first occurrence matching the identifier is returned. The outer variable remains untouched in the outer dictionary and becomes visible again as soon as the inner scope is popped.

**Q3: How are arrays and stacks distinguished from primitive types in your table?**  
*Answer:* The `SymbolInfo` record contains an `element_type` field and an optional `size` field. For primitive types like `Integer`, `element_type` is `None`. For `Array<Integer>`, `data_type` is `"Array<Integer>"` and `element_type` is `"Integer"`.

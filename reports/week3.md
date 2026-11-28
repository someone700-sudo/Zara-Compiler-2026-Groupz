# Week 3 Progress Report: Syntax Analysis – Top-Down Parsing

## 1. What Was Built
- Hand-written Recursive Descent Parser in `src/zara/parser/recursive_descent.py`.
- Complete AST class hierarchy in `src/zara/ast/nodes.py` (Program, VarDecl, FunctionDecl, ClassDecl, FieldDecl, MethodDecl, Block, Assignment, IfStmt, ForStmt, DoWhileStmt, ReturnStmt, PrintStmt, BinaryOp, Literals, Calls, Indexing, MemberAccess).
- Parsing support for:
  - Variable declarations with mandatory initialization.
  - Subprograms (functions and class methods).
  - Classes with single inheritance (`extends`).
  - Control structures (`if-else`, `for`, `do-while`).
  - Expressions with strict precedence climbing:
    - Multiplicative (`*`, `/`) > Subtractive (`-`) > Relational (`>`) > Equality (`==`).
  - Built-in `print` statement.
  - Collection expressions (array indexing `a[i]`, array literals `[1, 2, 3]`, object instantiation `new Class()`, stack instantiation `new Stack()`).
- Panic-mode error recovery synchronizing on semicolons (`;`) and block delimiters (`}`).
- AST pretty-printer function `format_ast()` for CLI inspection via `--ast`.

## 2. Design Choices
- **Precedence Climbing Architecture:** Expressions are parsed through layered helper methods (`parse_equality` calls `parse_comparison` calls `parse_subtraction` calls `parse_multiplication` calls `parse_primary`). This eliminates left recursion while maintaining left-associativity and correct operator precedence.
- **AST Decoupling:** The AST nodes are completely independent of parser implementation, allowing Week 4's Bottom-Up parser to produce identical AST structures.

## 3. Test Results
- Suite: `tests/test_parser.py`
- Executed 5 comprehensive unit tests:
  - Declarations across all Zara data types.
  - Operator precedence verification (e.g. `10 - 2 * 3` correctly structures `*` beneath `-`).
  - Control flow statements (`if-else`, `for`, `do-while`).
  - Class declarations with inheritance and functions.
  - Panic-mode recovery upon encountering syntax errors.
- All tests passed with 100% success.

## 4. Limitations
- Expressions only permit the six spec-defined operators. Expressions containing unauthorized operators like `+` trigger syntax/lexical error reporting.

## 5. How to Explain This (Viva Preparation)

### Talking Points
1. Top-down recursive descent is an LL(1) parsing technique where grammar productions are transcribed directly into recursive subroutines.
2. Left recursion in grammar rules must be eliminated (converted to iteration or precedence climbing) to prevent infinite loops.
3. Operator precedence is enforced structurally by nesting production functions from lowest precedence (`==`) to highest (`*`, `/`).
4. Abstract Syntax Trees (ASTs) discard non-semantic concrete syntax (such as commas and parentheses) while retaining structural intent.
5. Panic-mode synchronization allows the parser to recover from missing semicolons or malformed clauses and continue parsing subsequent statements.

### Key Algorithm: Precedence Climbing
```
Algorithm ParseSubtraction():
  node = ParseMultiplication()
  While current_token is MINUS:
      op = advance()
      right = ParseMultiplication()
      node = BinaryOp("-", node, right)
  Return node
```

### Likely Examiner Questions & Model Answers
**Q1: Why can't a recursive descent parser directly parse a grammar with left recursion?**  
*Answer:* A production of the form $E \to E - T$ causes a recursive descent parser to call `parse_E()` at the beginning of `parse_E()`, resulting in infinite recursion before any input tokens are consumed. We eliminate left recursion by transforming the rule into an iterative loop: $E \to T \{- T\}^*$.

**Q2: How does panic-mode error recovery work in your parser?**  
*Answer:* When an unexpected token is encountered, the parser logs a `ParseError` with line, column, and expected token in the `ErrorHandler`. It then enters panic mode and discards incoming tokens until a synchronizing token (such as `;` or `}`) or a statement-starting keyword is reached, where it resumes normal parsing.

**Q3: How does your parser distinguish a class variable declaration `Dog d = ...;` from an assignment or function call?**  
*Answer:* When encountering an identifier, the parser performs a two-token lookahead (LL(2) inspection). If the identifier is immediately followed by another identifier (e.g., `Dog d`), it parses the construct as a variable declaration of class type `Dog`. Otherwise, it treats it as an expression or assignment.

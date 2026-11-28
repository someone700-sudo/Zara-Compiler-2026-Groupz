# Week 2 Progress Report: Lexical Analysis

## 1. What Was Built
- Hand-crafted regex-based Lexical Analyzer in `src/zara/lexer/lexer.py`.
- Token specifications in `src/zara/lexer/tokens.py` implementing all token categories:
  - Literals: `INT_LIT`, `FLOAT_LIT`, `STRING_LIT`
  - Identifiers: `IDENT`
  - Type keywords: `Integer`, `Float`, `String`, `Array`, `Stack`
  - Control keywords: `if`, `else`, `do`, `while`, `for`
  - Subprograms & OOP: `function`, `return`, `class`, `extends`, `new`, `this`
  - Built-in I/O: `print`
  - The strict set of **six operators only**: `=`, `*`, `/`, `-`, `>`, `==`
  - Delimiters: `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `.`, `<`
- Comments handling: Single-line (`//...`) and multi-line (`/* ... */`).
- Error reporting & recovery in `src/zara/errors/error_handler.py`: illegal characters, unterminated strings, and unterminated block comments report exact line and column numbers.
- CLI formatting utility `--tokens` to print a formatted token stream table.

## 2. Design Choices
- **Precedence in Regex Matching:** Longest-match rule enforced: `==` before `=`, `Float` literal before `Int` literal followed by `.`.
- **Comment Handling:** Multi-line comments are intercepted before regex matching to accurately count embedded newlines and detect unterminated comments spanning files.
- **Error Recovery:** When an illegal character is encountered, a `CompilerError` is recorded, the bad character is skipped, and scanning continues to find further errors.

## 3. Test Results
- Suite: `tests/test_lexer.py`
- Executed 5 unit tests verifying: keyword and type tokenization, operator uniqueness (only the six allowed operators), integer/float/string literals, comment stripping, and error recovery on illegal characters and unterminated strings.
- All 5 tests passed cleanly.

## 4. Limitations
- Zara strictly permits only six operators. Unary minus is deliberately not tokenized as a separate operator; negative values must be parsed or written as expressions such as `0 - x`.

 5. How to Explain This (Viva Preparation)

### Talking Points
1. The lexer is the front-end phase that converts raw character streams into meaningful atomic units called tokens.
2. Regular expressions define the lexical grammar of Zara based on deterministic finite automata (DFA) theory.
3. Every token carries precise source coordinates (line and column numbers) used across all subsequent compiler phases.
4. Only the six allowed operators (`=`, `*`, `/`, `-`, `>`, `==`) are recognized; any foreign operator is flagged as an illegal character.
5. Comments and whitespace are discarded after updating line and column counters.
6. Lexical error recovery skips invalid input so that the entire file can be scanned in a single pass.

### Key Algorithm: Regex Scanner Loop
```
Algorithm Tokenize(source):
  1. Initialize pos = 0, line = 1, line_start = 0.
  2. While pos < length(source):
       a. Check for multi-line comment '/*':
          If found: scan to '*/', update line counts, set pos, continue.
       b. Match master regex at pos:
          - If NEWLINE: increment line, update line_start, advance pos.
          - If WHITESPACE or SL_COMMENT: advance pos.
          - If LITERAL / IDENT / KEYWORD / OPERATOR / DELIMITER:
              Compute column = pos - line_start + 1.
              Emit Token(type, value, line, col). Advance pos.
          - If MISMATCH (unrecognized char):
              Report Lexical Error. Advance pos by 1 (skip & recover).
  3. Emit Token(EOF, "", line, col).
```



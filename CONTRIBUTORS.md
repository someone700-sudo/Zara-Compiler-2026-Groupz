# Group Contribution Report

> **Note on Team Size:** Our group has 4 members. The course assignment specifies exactly 5; we have requested/are requesting an exemption from the course lecturer and are submitting transparently with 4 active contributors.

## Project: Zara Programming Language Compiler
## Course: CCS 3207 Compiler Construction — 2026

| # | Name | Registration Number | Responsibilities | Contribution Summary |
|---|------|---------------------|-----------------|---------------------|
| 1 | **Charlton Gikaria** | `C026-01-0804/2024` | Repository Baseline, Semantic Analysis (Wk 5), OOP Support (Wk 9), Project Coordination | Repository setup and baseline, multi-pass semantic analyzer, OOP inheritance resolution, and overall project coordination. |
| 2 | **Joel Kamande** | `C026-01-0742/2024` | Lexer (Wk 2), Syntax-Directed Translation (Wk 6), Code Generation (Wk 10) | Regex lexer with illegal character skipping, SDT attribute evaluation engine, and ZSVM bytecode generator. |
| 3 | **Stanley Kahuthu** | `C026-01-0759/2024` | AST & Recursive Descent Parser (Wk 3), TAC Generator (Wk 7), Error Handling & Integration (Wk 11) | AST node hierarchy, LL(1) recursive descent parser, Three-Address Code generator, and unified panic-mode error recovery. |
| 4 | **Neville Krop** | `C026-01-2417/2024` | Symbol Table (Wk 1), Bottom-Up Parser (Wk 4), Code Optimizer (Wk 8) | Scoped symbol table, bottom-up shift-reduce parser with conflict tracing, and constant folding / DCE / LICM optimizer. |

**Group Leader:** **Charlton Gikaria** (`C026-01-0804/2024`)

## Detailed Contributions

### Member 1: Charlton Gikaria (`C026-01-0804/2024`) (Leader)
- Week(s) primarily responsible for: Repository Baseline, Weeks 5, 9, Project Coordination
- Key modules implemented: Project repository baseline, `src/zara/semantic/analyzer.py`, OOP support in symbol table and AST
- Testing contributions: `tests/test_semantic.py`
- Documentation contributions: `reports/week5.md`, `reports/week9.md`, `docs/ARCHITECTURE.md`

### Member 2: Joel Kamande (`C026-01-0742/2024`)
- Week(s) primarily responsible for: Weeks 2, 6, 10
- Key modules implemented: `src/zara/lexer/tokens.py`, `src/zara/lexer/lexer.py`, `src/zara/translation/translator.py`, `src/zara/codegen/isa.py`, `src/zara/codegen/generator.py`
- Testing contributions: `tests/test_lexer.py`, `tests/test_sdt.py`, `tests/test_codegen.py`
- Documentation contributions: `reports/week2.md`, `reports/week6.md`, `reports/week10.md`, `docs/attribute_grammar.md`, `docs/target_isa.md`

### Member 3: Stanley Kahuthu (`C026-01-0759/2024`)
- Week(s) primarily responsible for: Weeks 3, 7, 11
- Key modules implemented: `src/zara/ast/nodes.py`, `src/zara/parser/recursive_descent.py`, `src/zara/ir/tac.py`, `src/zara/ir/tac_generator.py`, `src/zara/errors/error_handler.py`, `main.py`
- Testing contributions: `tests/test_parser.py`, `tests/test_tac.py`, `tests/run_tests.py`
- Documentation contributions: `reports/week3.md`, `reports/week7.md`, `reports/week11.md`, `docs/LANGUAGE_SPEC.md`

### Member 4: Neville Krop (`C026-01-2417/2024`)
- Week(s) primarily responsible for: Weeks 1, 4, 8
- Key modules implemented: `src/zara/symboltable/symbol_table.py`, `src/zara/parser/bottom_up.py`, `src/zara/ir/tac_interpreter.py`, `src/zara/optimizer/optimizer.py`
- Testing contributions: `tests/test_symbol_table.py`, `tests/test_bottom_up.py`, `tests/test_optimizer.py`
- Documentation contributions: `reports/week1.md`, `reports/week4.md`, `reports/week8.md`, `docs/optimizer_notes.md`

## Declaration

We declare that all 4 members have contributed meaningfully to this project throughout the 11-week period. All contributions are visible through the project's development history.

| Name | Registration Number| 
|------|---------------------||
| Charlton Gikaria | `C026-01-0804/2024` |
| Joel Kamande | `C026-01-0742/2024` |
| Stanley Kahuthu | `C026-01-0759/2024` |
| Neville Krop | `C026-01-2417/2024` |
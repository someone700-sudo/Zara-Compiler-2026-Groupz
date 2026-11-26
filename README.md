# Zara Programming Language Compiler

> **CCS 3207 Compiler Construction — 2026**  
> Design and Implementation of the Zara Programming Language Compiler

## Group Members

> **Note on Team Size:** Our group has 4 members. The course assignment specifies exactly 5; we have requested/are requesting an exemption from the course lecturer and are submitting transparently with 4 active contributors.

| # | Name | Registration Number | Responsibilities | Group Leader |
|---|------|---------------------|-----------------|--------------|
| 1 | **Charlton Gikaria** | `C026-01-0804/2024` | Repository Baseline, Semantic Analysis (Wk 5), OOP Support (Wk 9), Project Coordination | ✅ |
| 2 | **Joel Kamande** | `C026-01-0742/2024` | Lexer (Wk 2), Syntax-Directed Translation (Wk 6), Code Generation (Wk 10) | |
| 3 | **Stanley Kahuthu** | `C026-01-0759/2024` | AST & Recursive Descent Parser (Wk 3), TAC Generator (Wk 7), Error Handling & Integration (Wk 11) | |
| 4 | **Neville Krop** | `C026-01-2417/2024` | Symbol Table (Wk 1), Bottom-Up Parser (Wk 4), Code Optimizer (Wk 8) | |

**Group Leader:** **Charlton Gikaria** (`C026-01-0804/2024`)

## Project Setup

### Prerequisites

- **Python 3.10 or higher** (standard library only — no external packages)
- No parser generators (no PLY, ANTLR, Lark, yacc)
- All components are hand-written

### Installation

```bash
# No installation needed. Clone the repository and run directly.
# Verify Python version:
python --version   # Must be 3.10+
```

### Running the Compiler

```bash
# Full compilation pipeline
python main.py program.zara

# Individual phase outputs
python main.py program.zara --tokens        # Lexical analysis token table
python main.py program.zara --ast           # Abstract Syntax Tree
python main.py program.zara --parse-trace   # Bottom-up parser trace
python main.py program.zara --symbols       # Symbol table dump
python main.py program.zara --semantic      # Semantic analysis report
python main.py program.zara --attributes    # SDT attribute values
python main.py program.zara --tac           # Three-Address Code
python main.py program.zara --optimized     # Optimized TAC (before/after)
python main.py program.zara --target        # Target VM instructions
python main.py program.zara --run           # Execute and show output
python main.py program.zara --all           # Show all phases

# Symbol table standalone demo
python main.py --demo-symbols
```

### Running Tests

```bash
python tests/run_tests.py
```

## Supported Zara Language Features

### Data Types
- `Integer` — whole numbers
- `Float` — decimal numbers
- `String` — character sequences
- `Array<T>` — ordered indexed collections
- `Stack<T>` — LIFO data structures with push/pop/peek/isEmpty

### Operators (exactly six)
| Operator | Description |
|----------|-------------|
| `=` | Assignment |
| `*` | Multiplication |
| `/` | Division |
| `-` | Subtraction |
| `>` | Greater than (yields Integer 1 or 0) |
| `==` | Equality (yields Integer 1 or 0) |

### Control Structures
- `if-else` conditional
- `for` loop
- `do-while` loop

### Subprograms
- Functions with typed parameters and return values
- Methods within classes

### Object-Oriented Features
- Classes and objects
- Single inheritance (`extends`)
- Method overriding
- `this` keyword
- `new` for object/stack creation

### Built-ins
- `print(expr)` — output a value
- Array indexing (`a[i]`), length (`a.length`)
- Stack operations (`push`, `pop`, `peek`, `isEmpty`)

## Architecture

```
Source (.zara)
    │
    ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Lexer   │───▶│  Parser  │───▶│ Semantic │───▶│   SDT    │
│ (Week 2) │    │(Wk 3+4) │    │ (Week 5) │    │ (Week 6) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
    │   VM     │◀───│ Code Gen │◀───│Optimizer │◀────┘
    │(Week 10) │    │(Week 10) │    │ (Week 8) │
    └──────────┘    └──────────┘    └──────────┘
                                        ▲
                                   ┌──────────┐
                                   │   TAC    │
                                   │ (Week 7) │
                                   └──────────┘
```

## Week-to-Module Mapping

| Week | Module | Key Files |
|------|--------|-----------|
| 1 | Symbol Table | `src/zara/symboltable/` |
| 2 | Lexer | `src/zara/lexer/` |
| 3 | Recursive Descent Parser | `src/zara/parser/recursive_descent.py`, `src/zara/ast/` |
| 4 | Bottom-Up Parser | `src/zara/parser/bottom_up.py` |
| 5 | Semantic Analyzer | `src/zara/semantic/` |
| 6 | SDT | `src/zara/translation/` |
| 7 | TAC | `src/zara/ir/` |
| 8 | Optimizer | `src/zara/optimizer/` |
| 9 | OOP | Updates across symboltable, semantic, ir, parser |
| 10 | Code Gen + VM | `src/zara/codegen/` |
| 11 | Errors + Integration | `src/zara/errors/`, `main.py` |

## Documentation

- [Language Specification](docs/LANGUAGE_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Technical Report](docs/technical_report.md)
- [Assignment Analysis](docs/ASSIGNMENT_ANALYSIS.md)

## License

Academic project for CCS 3207 Compiler Construction, 2026.

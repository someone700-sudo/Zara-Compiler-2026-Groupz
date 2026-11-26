#!/usr/bin/env python3
"""
Main entry point and CLI driver for the Zara Programming Language Compiler.
Course: CCS 3207 Compiler Construction - 2026

Usage:
  python main.py <source_file.zara> [flags]
  python main.py --demo-symbols

Flags:
  --tokens        Print the lexical token table
  --ast           Print the Abstract Syntax Tree (AST)
  --parse-trace   Print bottom-up shift-reduce parse trace & conflicts
  --symbols       Print the populated symbol table
  --semantic      Print semantic analysis diagnostic report
  --attributes    Print Syntax-Directed Translation (SDT) attributes
  --tac           Print Three-Address Code (TAC)
  --optimized     Print unoptimized vs optimized TAC with metrics
  --target        Print target assembly code (ZSVM bytecode)
  --run           Execute compiled program on the virtual machine
  --all           Run and display output from all compiler phases
  --demo-symbols  Run standalone symbol table demonstration (Week 1)
"""

import sys
import os
import argparse

# Ensure src/ is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from zara.errors.error_handler import ErrorHandler, ErrorPhase
from zara.symboltable.symbol_table import SymbolTable, demo_symbol_table
from zara.lexer.lexer import Lexer
from zara.ast.nodes import format_ast
from zara.parser.recursive_descent import RecursiveDescentParser
from zara.parser.bottom_up import BottomUpParser
from zara.semantic.analyzer import SemanticAnalyzer
from zara.translation.translator import SDTTranslator
from zara.ir.tac_generator import TACGenerator
from zara.ir.tac_interpreter import TACInterpreter
from zara.optimizer.optimizer import TACOptimizer
from zara.codegen.generator import CodeGenerator
from zara.codegen.vm import ZaraVM


def run_pipeline(source_code: str, args: argparse.Namespace) -> int:
    """Execute the Zara compilation pipeline according to specified flags."""
    error_handler = ErrorHandler()

    # Phase 1: Lexical Analysis
    lexer = Lexer(error_handler)
    tokens = lexer.tokenize(source_code)

    if args.tokens or args.all:
        print(lexer.format_tokens(tokens))

    # Phase 2: Syntax Analysis (Recursive Descent + Bottom-Up)
    rd_parser = RecursiveDescentParser(tokens, error_handler)
    ast = rd_parser.parse()

    if args.ast or args.all:
        print("\n" + "=" * 60)
        print("  ABSTRACT SYNTAX TREE (AST)")
        print("=" * 60)
        print(format_ast(ast))

    if args.parse_trace or args.all:
        bu_parser = BottomUpParser(tokens, error_handler)
        bu_parser.parse()
        print(bu_parser.format_trace())
        print(bu_parser.format_conflicts())

    # Phase 3: Semantic Analysis
    analyzer = SemanticAnalyzer(error_handler)
    symbol_table = analyzer.analyze(ast)

    if args.symbols or args.all:
        print(symbol_table.format_table())

    if args.semantic or args.all:
        print("\n" + "=" * 60)
        print("  SEMANTIC ANALYSIS REPORT")
        print("=" * 60)
        semantic_errors = error_handler.get_errors(ErrorPhase.SEMANTIC)
        if semantic_errors:
            for i, err in enumerate(semantic_errors, 1):
                print(f"  {i}. {err}")
        else:
            print("  Semantic analysis completed with 0 errors. All types and scopes verified.")
        print("=" * 60)

    # Check for compile-time errors
    if error_handler.has_errors():
        print(error_handler.format_errors())
        print("\n" + error_handler.format_summary())
        return 1

    # Phase 4: Syntax-Directed Translation (SDT)
    translator = SDTTranslator()
    translated_ast = translator.translate(ast)

    if args.attributes or args.all:
        print(translator.format_attribute_trace())

    # Phase 5: Three-Address Code (TAC) Generation
    tac_gen = TACGenerator()
    tac_prog = tac_gen.generate(translated_ast)

    if args.tac or args.all:
        print(tac_prog.format_code())

    # Phase 6: Code Optimization
    optimizer = TACOptimizer()
    opt_tac, opt_report = optimizer.optimize(tac_prog)

    if args.optimized or args.all:
        print(opt_report.format_report(tac_prog, opt_tac))

    # Phase 7: Target Code Generation (ZSVM Bytecode)
    code_gen = CodeGenerator()
    target_instructions = code_gen.generate(opt_tac)

    if args.target or args.all:
        print(code_gen.format_target_code())

    # Phase 8: Execution on Virtual Machine
    if args.run or args.all:
        print("\n" + "=" * 60)
        print("  PROGRAM EXECUTION OUTPUT (ZSVM)")
        print("=" * 60)
        vm = ZaraVM(target_instructions, class_parents=code_gen.class_parents)
        output = vm.execute()
        if output:
            print(output)
        else:
            print("  (Program executed successfully with no printed output)")
        print("=" * 60)

    # Default action if no flags provided: compile and run
    if not any([args.tokens, args.ast, args.parse_trace, args.symbols,
                args.semantic, args.attributes, args.tac, args.optimized,
                args.target, args.run, args.all]):
        vm = ZaraVM(target_instructions, class_parents=code_gen.class_parents)
        output = vm.execute()
        if output:
            print(output)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Zara Programming Language Compiler (CCS 3207)"
    )
    parser.add_argument("source", nargs="?", help="Path to Zara source file (.zara)")
    parser.add_argument("--tokens", action="store_true", help="Print token table")
    parser.add_argument("--ast", action="store_true", help="Print Abstract Syntax Tree")
    parser.add_argument("--parse-trace", action="store_true", help="Print shift-reduce trace & conflicts")
    parser.add_argument("--symbols", action="store_true", help="Print symbol table")
    parser.add_argument("--semantic", action="store_true", help="Print semantic analysis report")
    parser.add_argument("--attributes", action="store_true", help="Print SDT synthesized attributes")
    parser.add_argument("--tac", action="store_true", help="Print Three-Address Code")
    parser.add_argument("--optimized", action="store_true", help="Print optimization comparison")
    parser.add_argument("--target", action="store_true", help="Print target VM instructions")
    parser.add_argument("--run", action="store_true", help="Execute on target VM and show output")
    parser.add_argument("--all", action="store_true", help="Run all phases with full diagnostic output")
    parser.add_argument("--demo-symbols", action="store_true", help="Run standalone symbol table demo")

    args = parser.parse_args()

    if args.demo_symbols:
        demo_symbol_table()
        return 0

    if not args.source:
        parser.print_help()
        print("\nError: Please provide a .zara source file or specify --demo-symbols.")
        return 1

    if not os.path.exists(args.source):
        print(f"Error: Source file '{args.source}' not found.")
        return 1

    with open(args.source, "r", encoding="utf-8") as f:
        source_code = f.read()

    return run_pipeline(source_code, args)


if __name__ == "__main__":
    sys.exit(main())

"""
Recursive Descent Parser for the Zara Language (Week 3).

Hand-written LL(1) recursive descent parser with left recursion eliminated.
Supports:
  - Types: Primitive, Generic Array<T>, Generic Stack<T>, Class types
  - Declarations: Classes (with single inheritance), Methods, Fields, Functions, Variables
  - Statements: Block, VarDecl, Assignment, If-Else, For, Do-While, Return, Print, ExprStmt
  - Expressions with correct precedence:
      Parentheses, Indexing, Member Access / Calls
      * /   (highest arithmetic)
      -     (subtraction)
      >     (relational comparison)
      ==    (equality)
      =     (assignment statement)
  - Panic-mode error recovery synchronizing on ';' and '}'.
"""

from typing import List, Optional, Tuple, Any
from zara.lexer.tokens import Token, TokenType
from zara.ast.nodes import (
    ASTNode, Program, TypeNode, VarDecl, FunctionDecl, ClassDecl,
    FieldDecl, MethodDecl, Param, Block, Assignment, IfStmt, ForStmt,
    DoWhileStmt, ReturnStmt, PrintStmt, ExprStmt, BinaryOp, IntLiteral,
    FloatLiteral, StringLiteral, Identifier, ArrayLiteral, ArrayAccess,
    MemberAccess, FunctionCall, MethodCall, NewObject, NewStack, ThisExpr
)
from zara.errors.error_handler import ErrorHandler, ErrorPhase


class ParseError(Exception):
    """Internal exception raised during parsing to trigger recovery."""
    pass


class RecursiveDescentParser:
    """
    Recursive descent LL(1) parser for Zara.
    Constructs an Abstract Syntax Tree (AST).
    """

    def __init__(self, tokens: List[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.errors = error_handler
        self.pos = 0

    # ----------------------------------------------------------------------
    # Helper navigation methods
    # ----------------------------------------------------------------------

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek_token(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current_token()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def match(self, *expected_types: TokenType) -> bool:
        if self.current_token().type in expected_types:
            self.advance()
            return True
        return False

    def expect(self, expected_type: TokenType, suggestion: Optional[str] = None) -> Token:
        tok = self.current_token()
        if tok.type == expected_type:
            return self.advance()
        msg = f"Expected '{expected_type.name}', but found '{tok.value}' ({tok.type.name})"
        self.errors.report(ErrorPhase.PARSER, tok.line, tok.col, msg, suggestion)
        raise ParseError(msg)

    # ----------------------------------------------------------------------
    # Panic-mode error recovery
    # ----------------------------------------------------------------------

    def synchronize(self) -> None:
        """
        Advance tokens until a synchronization point (semicolon, closing brace,
        or major declaration keyword) is found.
        """
        self.errors.enter_panic_mode()
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.SEMICOLON:
                self.advance()
                self.errors.exit_panic_mode()
                return
            if self.current_token().type == TokenType.RBRACE:
                self.advance()
                self.errors.exit_panic_mode()
                return
            if self.current_token().type in (
                TokenType.KW_CLASS, TokenType.KW_FUNCTION, TokenType.KW_IF,
                TokenType.KW_FOR, TokenType.KW_DO, TokenType.KW_RETURN,
                TokenType.KW_PRINT, TokenType.KW_INTEGER, TokenType.KW_FLOAT,
                TokenType.KW_STRING, TokenType.KW_ARRAY, TokenType.KW_STACK
            ):
                self.errors.exit_panic_mode()
                return
            self.advance()
        self.errors.exit_panic_mode()

    # ----------------------------------------------------------------------
    # Entry Point
    # ----------------------------------------------------------------------

    def parse(self) -> Program:
        """Parse program root: Program = { TopLevelDecl } ;"""
        decls: List[ASTNode] = []
        start_tok = self.current_token()

        while self.current_token().type != TokenType.EOF:
            try:
                decl = self.parse_top_level_decl()
                if decl is not None:
                    decls.append(decl)
            except ParseError:
                self.synchronize()

        return Program(decls, line=start_tok.line, col=start_tok.col)

    def parse_top_level_decl(self) -> Optional[ASTNode]:
        tok = self.current_token()
        if tok.type == TokenType.KW_CLASS:
            return self.parse_class_decl()
        elif tok.type == TokenType.KW_FUNCTION:
            return self.parse_function_decl()
        else:
            return self.parse_statement()

    # ----------------------------------------------------------------------
    # Declarations
    # ----------------------------------------------------------------------

    def parse_type(self) -> TypeNode:
        tok = self.current_token()
        if tok.type in (TokenType.KW_INTEGER, TokenType.KW_FLOAT, TokenType.KW_STRING):
            self.advance()
            return TypeNode(tok.value, line=tok.line, col=tok.col)
        elif tok.type in (TokenType.KW_ARRAY, TokenType.KW_STACK):
            base_type = tok.value
            self.advance()
            self.expect(TokenType.LT, "Generic type requires opening '<', e.g. Array<Integer>")
            elem_tok = self.current_token()
            if elem_tok.type in (TokenType.KW_INTEGER, TokenType.KW_FLOAT, TokenType.KW_STRING, TokenType.IDENT):
                elem_type = elem_tok.value
                self.advance()
            else:
                msg = f"Expected element type in {base_type}<...>, found '{elem_tok.value}'"
                self.errors.report(ErrorPhase.PARSER, elem_tok.line, elem_tok.col, msg)
                elem_type = "Integer"
            self.expect(TokenType.GT, "Generic type requires closing '>', e.g. Array<Integer>")
            return TypeNode(base_type, element_type=elem_type, line=tok.line, col=tok.col)
        elif tok.type == TokenType.IDENT:
            self.advance()
            return TypeNode(tok.value, line=tok.line, col=tok.col)
        else:
            msg = f"Expected type, but found '{tok.value}'"
            self.errors.report(ErrorPhase.PARSER, tok.line, tok.col, msg, "Use Integer, Float, String, Array<T>, Stack<T>, or ClassName")
            raise ParseError(msg)

    def is_type_start(self, tok: Token) -> bool:
        if tok.type in (TokenType.KW_INTEGER, TokenType.KW_FLOAT, TokenType.KW_STRING, TokenType.KW_ARRAY, TokenType.KW_STACK):
            return True
        if tok.type == TokenType.IDENT:
            # Check if next token is also an identifier (e.g. `Dog d = ...`)
            return self.peek_token(1).type == TokenType.IDENT
        return False

    def parse_class_decl(self) -> ClassDecl:
        tok = self.expect(TokenType.KW_CLASS)
        name_tok = self.expect(TokenType.IDENT, "Expected class name identifier")
        parent_name: Optional[str] = None
        if self.match(TokenType.KW_EXTENDS):
            parent_tok = self.expect(TokenType.IDENT, "Expected superclass name identifier after 'extends'")
            parent_name = parent_tok.value

        self.expect(TokenType.LBRACE, "Expected '{' to begin class body")
        members: List[ASTNode] = []
        while self.current_token().type not in (TokenType.RBRACE, TokenType.EOF):
            try:
                member = self.parse_class_member()
                if member:
                    members.append(member)
            except ParseError:
                self.synchronize()

        self.expect(TokenType.RBRACE, "Expected '}' to close class body")
        return ClassDecl(name_tok.value, parent_name, members, line=tok.line, col=tok.col)

    def parse_class_member(self) -> ASTNode:
        """Parse field or method in class."""
        typ = self.parse_type()
        name_tok = self.expect(TokenType.IDENT, "Expected field or method identifier")

        if self.current_token().type == TokenType.LPAREN:
            # Method declaration: Type name ( params ) { ... }
            self.advance()
            params = self.parse_param_list()
            self.expect(TokenType.RPAREN, "Expected ')' after parameter list")
            body = self.parse_block()
            return MethodDecl(typ, name_tok.value, params, body, line=name_tok.line, col=name_tok.col)
        else:
            # Field declaration: Type name ;
            self.expect(TokenType.SEMICOLON, "Expected ';' after field declaration")
            return FieldDecl(typ, name_tok.value, line=name_tok.line, col=name_tok.col)

    def parse_function_decl(self) -> FunctionDecl:
        tok = self.expect(TokenType.KW_FUNCTION)
        ret_type = self.parse_type()
        name_tok = self.expect(TokenType.IDENT, "Expected function name identifier")
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        params = self.parse_param_list()
        self.expect(TokenType.RPAREN, "Expected ')' after parameter list")
        body = self.parse_block()
        return FunctionDecl(ret_type, name_tok.value, params, body, line=tok.line, col=tok.col)

    def parse_param_list(self) -> List[Param]:
        params: List[Param] = []
        if self.current_token().type == TokenType.RPAREN:
            return params

        p_type = self.parse_type()
        p_name = self.expect(TokenType.IDENT, "Expected parameter name")
        params.append(Param(p_type, p_name.value, line=p_name.line, col=p_name.col))

        while self.match(TokenType.COMMA):
            p_type = self.parse_type()
            p_name = self.expect(TokenType.IDENT, "Expected parameter name")
            params.append(Param(p_type, p_name.value, line=p_name.line, col=p_name.col))

        return params

    # ----------------------------------------------------------------------
    # Statements
    # ----------------------------------------------------------------------

    def parse_block(self) -> Block:
        tok = self.expect(TokenType.LBRACE, "Expected '{' to start block")
        stmts: List[ASTNode] = []
        while self.current_token().type not in (TokenType.RBRACE, TokenType.EOF):
            try:
                stmt = self.parse_statement()
                if stmt:
                    stmts.append(stmt)
            except ParseError:
                self.synchronize()
        self.expect(TokenType.RBRACE, "Expected '}' to end block")
        return Block(stmts, line=tok.line, col=tok.col)

    def parse_statement(self) -> ASTNode:
        tok = self.current_token()

        if tok.type == TokenType.LBRACE:
            return self.parse_block()
        elif tok.type == TokenType.KW_IF:
            return self.parse_if_stmt()
        elif tok.type == TokenType.KW_FOR:
            return self.parse_for_stmt()
        elif tok.type == TokenType.KW_DO:
            return self.parse_do_while_stmt()
        elif tok.type == TokenType.KW_RETURN:
            return self.parse_return_stmt()
        elif tok.type == TokenType.KW_PRINT:
            return self.parse_print_stmt()
        elif self.is_type_start(tok):
            return self.parse_var_decl()
        else:
            return self.parse_assign_or_expr_stmt()

    def parse_var_decl(self) -> VarDecl:
        typ = self.parse_type()
        name_tok = self.expect(TokenType.IDENT, "Expected variable name in declaration")
        self.expect(TokenType.ASSIGN, "Expected '=' in variable declaration (initialization is required)")
        init_expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDecl(typ, name_tok.value, init_expr, line=typ.line, col=typ.col)

    def parse_assign_or_expr_stmt(self) -> ASTNode:
        start_tok = self.current_token()
        expr = self.parse_expr()

        if self.match(TokenType.ASSIGN):
            # Assignment statement: LValue = Expr ;
            val_expr = self.parse_expr()
            self.expect(TokenType.SEMICOLON, "Expected ';' after assignment")
            return Assignment(expr, val_expr, line=start_tok.line, col=start_tok.col)

        self.expect(TokenType.SEMICOLON, "Expected ';' after statement")
        return ExprStmt(expr, line=start_tok.line, col=start_tok.col)

    def parse_if_stmt(self) -> IfStmt:
        tok = self.expect(TokenType.KW_IF)
        self.expect(TokenType.LPAREN, "Expected '(' after 'if'")
        cond = self.parse_expr()
        self.expect(TokenType.RPAREN, "Expected ')' after if condition")
        then_block = self.parse_block()
        else_block: Optional[Block] = None
        if self.match(TokenType.KW_ELSE):
            if self.current_token().type == TokenType.KW_IF:
                # else if chained
                nested_if = self.parse_if_stmt()
                else_block = Block([nested_if], line=nested_if.line, col=nested_if.col)
            else:
                else_block = self.parse_block()
        return IfStmt(cond, then_block, else_block, line=tok.line, col=tok.col)

    def parse_for_stmt(self) -> ForStmt:
        tok = self.expect(TokenType.KW_FOR)
        self.expect(TokenType.LPAREN, "Expected '(' after 'for'")

        # Init: VarDecl or Assignment
        if self.is_type_start(self.current_token()):
            typ = self.parse_type()
            name_tok = self.expect(TokenType.IDENT, "Expected variable name in for init")
            self.expect(TokenType.ASSIGN, "Expected '=' in for init declaration")
            init_val = self.parse_expr()
            self.expect(TokenType.SEMICOLON, "Expected ';' after for init")
            init_stmt: ASTNode = VarDecl(typ, name_tok.value, init_val, line=typ.line, col=typ.col)
        else:
            target = self.parse_primary()
            self.expect(TokenType.ASSIGN, "Expected '=' in for init assignment")
            val = self.parse_expr()
            self.expect(TokenType.SEMICOLON, "Expected ';' after for init")
            init_stmt = Assignment(target, val, line=target.line, col=target.col)

        # Condition
        cond = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "Expected ';' after for condition")

        # Update: Assignment without trailing semicolon
        target_up = self.parse_primary()
        self.expect(TokenType.ASSIGN, "Expected '=' in for update")
        val_up = self.parse_expr()
        update_stmt = Assignment(target_up, val_up, line=target_up.line, col=target_up.col)

        self.expect(TokenType.RPAREN, "Expected ')' after for clauses")
        body = self.parse_block()
        return ForStmt(init_stmt, cond, update_stmt, body, line=tok.line, col=tok.col)

    def parse_do_while_stmt(self) -> DoWhileStmt:
        tok = self.expect(TokenType.KW_DO)
        body = self.parse_block()
        self.expect(TokenType.KW_WHILE, "Expected 'while' after do block")
        self.expect(TokenType.LPAREN, "Expected '(' after 'while'")
        cond = self.parse_expr()
        self.expect(TokenType.RPAREN, "Expected ')' after do-while condition")
        self.expect(TokenType.SEMICOLON, "Expected ';' after do-while condition")
        return DoWhileStmt(body, cond, line=tok.line, col=tok.col)

    def parse_return_stmt(self) -> ReturnStmt:
        tok = self.expect(TokenType.KW_RETURN)
        val = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "Expected ';' after return expression")
        return ReturnStmt(val, line=tok.line, col=tok.col)

    def parse_print_stmt(self) -> PrintStmt:
        tok = self.expect(TokenType.KW_PRINT)
        self.expect(TokenType.LPAREN, "Expected '(' after print")
        val = self.parse_expr()
        self.expect(TokenType.RPAREN, "Expected ')' after print argument")
        self.expect(TokenType.SEMICOLON, "Expected ';' after print(...)")
        return PrintStmt(val, line=tok.line, col=tok.col)

    # ----------------------------------------------------------------------
    # Expressions (Precedence Climbing)
    # Correct Zara Precedence:
    #   Level 1 (Lowest): ==
    #   Level 2: >
    #   Level 3: -
    #   Level 4: * /
    #   Level 5 (Highest): Primary, Postfix (calls, index, member access)
    # ----------------------------------------------------------------------

    def parse_expr(self) -> ASTNode:
        return self.parse_equality()

    def parse_equality(self) -> ASTNode:
        node = self.parse_comparison()
        while self.match(TokenType.EQ_EQ):
            op_tok = self.tokens[self.pos - 1]
            right = self.parse_comparison()
            node = BinaryOp("==", node, right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_comparison(self) -> ASTNode:
        node = self.parse_subtraction()
        while self.match(TokenType.GT):
            op_tok = self.tokens[self.pos - 1]
            right = self.parse_subtraction()
            node = BinaryOp(">", node, right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_subtraction(self) -> ASTNode:
        node = self.parse_multiplication()
        while self.match(TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            right = self.parse_multiplication()
            node = BinaryOp("-", node, right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_multiplication(self) -> ASTNode:
        node = self.parse_primary()
        while self.current_token().type in (TokenType.STAR, TokenType.SLASH):
            op_tok = self.advance()
            right = self.parse_primary()
            node = BinaryOp(op_tok.value, node, right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_primary(self) -> ASTNode:
        tok = self.current_token()

        if tok.type == TokenType.INT_LIT:
            self.advance()
            node: ASTNode = IntLiteral(int(tok.value), line=tok.line, col=tok.col)
        elif tok.type == TokenType.FLOAT_LIT:
            self.advance()
            node = FloatLiteral(float(tok.value), line=tok.line, col=tok.col)
        elif tok.type == TokenType.STRING_LIT:
            self.advance()
            # Strip enclosing quotes
            val = tok.value
            if val.startswith('"') and val.endswith('"') and len(val) >= 2:
                val = val[1:-1]
            node = StringLiteral(val, line=tok.line, col=tok.col)
        elif tok.type == TokenType.KW_THIS:
            self.advance()
            node = ThisExpr(line=tok.line, col=tok.col)
        elif tok.type == TokenType.KW_NEW:
            node = self.parse_new_expr()
        elif tok.type == TokenType.LBRACKET:
            node = self.parse_array_literal()
        elif tok.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expr()
            self.expect(TokenType.RPAREN, "Expected ')' after grouped expression")
        elif tok.type == TokenType.IDENT:
            self.advance()
            node = Identifier(tok.value, line=tok.line, col=tok.col)
        else:
            msg = f"Unexpected token in expression: '{tok.value}' ({tok.type.name})"
            self.errors.report(ErrorPhase.PARSER, tok.line, tok.col, msg)
            raise ParseError(msg)

        # Handle postfix operations: member access, indexing, calls
        return self.parse_postfix(node)

    def parse_new_expr(self) -> ASTNode:
        tok = self.expect(TokenType.KW_NEW)
        cls_tok = self.current_token()
        if cls_tok.type == TokenType.KW_STACK:
            self.advance()
            self.expect(TokenType.LPAREN, "Expected '(' after 'new Stack'")
            self.expect(TokenType.RPAREN, "Expected ')' after 'new Stack('")
            return NewStack(line=tok.line, col=tok.col)
        elif cls_tok.type == TokenType.IDENT:
            self.advance()
            self.expect(TokenType.LPAREN, f"Expected '(' after 'new {cls_tok.value}'")
            self.expect(TokenType.RPAREN, f"Expected ')' after 'new {cls_tok.value}('")
            return NewObject(cls_tok.value, line=tok.line, col=tok.col)
        else:
            msg = f"Expected class name or Stack after 'new', found '{cls_tok.value}'"
            self.errors.report(ErrorPhase.PARSER, cls_tok.line, cls_tok.col, msg)
            raise ParseError(msg)

    def parse_array_literal(self) -> ArrayLiteral:
        tok = self.expect(TokenType.LBRACKET)
        elems: List[ASTNode] = []
        if self.current_token().type != TokenType.RBRACKET:
            elems.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                elems.append(self.parse_expr())
        self.expect(TokenType.RBRACKET, "Expected ']' at end of array literal")
        return ArrayLiteral(elems, line=tok.line, col=tok.col)

    def parse_postfix(self, base: ASTNode) -> ASTNode:
        node = base
        while True:
            if self.match(TokenType.LBRACKET):
                idx = self.parse_expr()
                self.expect(TokenType.RBRACKET, "Expected ']' after array index")
                node = ArrayAccess(node, idx, line=node.line, col=node.col)
            elif self.match(TokenType.DOT):
                member_tok = self.expect(TokenType.IDENT, "Expected member name after '.'")
                # Could be a method call, e.g. obj.speak() or st.push(x)
                if self.match(TokenType.LPAREN):
                    args = self.parse_arg_list()
                    self.expect(TokenType.RPAREN, "Expected ')' after method arguments")
                    node = MethodCall(node, member_tok.value, args, line=member_tok.line, col=member_tok.col)
                else:
                    node = MemberAccess(node, member_tok.value, line=member_tok.line, col=member_tok.col)
            elif self.match(TokenType.LPAREN):
                # Function call on identifier
                args = self.parse_arg_list()
                self.expect(TokenType.RPAREN, "Expected ')' after function arguments")
                node = FunctionCall(node, args, line=node.line, col=node.col)
            else:
                break
        return node

    def parse_arg_list(self) -> List[ASTNode]:
        args: List[ASTNode] = []
        if self.current_token().type != TokenType.RPAREN:
            args.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expr())
        return args

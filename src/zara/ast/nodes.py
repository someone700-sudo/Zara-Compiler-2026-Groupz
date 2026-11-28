"""
AST (Abstract Syntax Tree) node definitions for the Zara language.

WHY: The AST is the central data structure passed between compiler phases.
The lexer produces tokens; the parser builds this tree; the semantic analyzer
annotates it; the translator attaches SDT attributes; the TAC generator walks
it to emit three-address code.  Every node records its source position
(line, col) so error messages stay accurate through every phase.

DESIGN: Each concrete node inherits from ASTNode and defines:
  - node_attrs()    -> dict of simple display attributes (name, op, value)
  - node_children() -> list of (label, child-or-list) for tree printing
This lets a single generic format_ast() function pretty-print any tree.
"""

from typing import List, Optional, Any


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col
        # SDT attributes (populated by the translator, Week 6)
        self.sdt_place: Optional[str] = None
        self.sdt_code: Optional[list] = None
        self.sdt_type: Optional[str] = None
        self.sdt_truelabel: Optional[str] = None
        self.sdt_falselabel: Optional[str] = None

    def node_name(self) -> str:
        return self.__class__.__name__

    def node_attrs(self) -> dict:
        """Simple key-value attributes to show on the node line."""
        return {}

    def node_children(self) -> list:
        """List of (label, child_node_or_list) for recursive printing."""
        return []


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class TypeNode(ASTNode):
    """
    Represents a Zara type, e.g. Integer, Array<Float>, Stack<Integer>, Dog.
    base_type  : 'Integer' | 'Float' | 'String' | 'Array' | 'Stack' | <ClassName>
    element_type: set for generic collections, e.g. 'Integer' in Array<Integer>
    """

    def __init__(self, base_type: str, element_type: Optional[str] = None,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.base_type = base_type
        self.element_type = element_type

    def type_str(self) -> str:
        """Human-readable type string, e.g. 'Array<Integer>'."""
        if self.element_type:
            return f"{self.base_type}<{self.element_type}>"
        return self.base_type

    def node_attrs(self) -> dict:
        return {"type": self.type_str()}

    def __repr__(self) -> str:
        return f"TypeNode({self.type_str()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeNode):
            return NotImplemented
        return (self.base_type == other.base_type and
                self.element_type == other.element_type)


# ---------------------------------------------------------------------------
# Program (root)
# ---------------------------------------------------------------------------

class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.declarations = declarations

    def node_children(self) -> list:
        return [("declarations", self.declarations)]


# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------

class VarDecl(ASTNode):
    """Variable declaration: Type name = initializer ;"""

    def __init__(self, var_type: TypeNode, name: str,
                 initializer: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def node_attrs(self) -> dict:
        return {"name": self.name, "type": self.var_type.type_str()}

    def node_children(self) -> list:
        return [("initializer", self.initializer)]


class FunctionDecl(ASTNode):
    """function ReturnType name(params) { body }"""

    def __init__(self, return_type: TypeNode, name: str,
                 params: list, body: "Block",
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.return_type = return_type
        self.name = name
        self.params = params   # list of Param
        self.body = body

    def node_attrs(self) -> dict:
        return {"name": self.name,
                "return_type": self.return_type.type_str()}

    def node_children(self) -> list:
        return [("params", self.params), ("body", self.body)]


class ClassDecl(ASTNode):
    """class Name [extends Parent] { members }"""

    def __init__(self, name: str, parent_name: Optional[str],
                 members: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.parent_name = parent_name
        self.members = members  # list of FieldDecl | MethodDecl

    def node_attrs(self) -> dict:
        d: dict = {"name": self.name}
        if self.parent_name:
            d["extends"] = self.parent_name
        return d

    def node_children(self) -> list:
        return [("members", self.members)]


class FieldDecl(ASTNode):
    """Field declaration inside a class: Type name ;"""

    def __init__(self, field_type: TypeNode, name: str,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.field_type = field_type
        self.name = name

    def node_attrs(self) -> dict:
        return {"name": self.name, "type": self.field_type.type_str()}


class MethodDecl(ASTNode):
    """Method inside a class: ReturnType name(params) { body }"""

    def __init__(self, return_type: TypeNode, name: str,
                 params: list, body: "Block",
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

    def node_attrs(self) -> dict:
        return {"name": self.name,
                "return_type": self.return_type.type_str()}

    def node_children(self) -> list:
        return [("params", self.params), ("body", self.body)]


class Param(ASTNode):
    """Function / method parameter: Type name"""

    def __init__(self, param_type: TypeNode, name: str,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.param_type = param_type
        self.name = name

    def node_attrs(self) -> dict:
        return {"name": self.name, "type": self.param_type.type_str()}


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

class Block(ASTNode):
    """{ statement* }"""

    def __init__(self, statements: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements

    def node_children(self) -> list:
        return [("statements", self.statements)]


class Assignment(ASTNode):
    """target = value ;"""

    def __init__(self, target: ASTNode, value: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.target = target
        self.value = value

    def node_children(self) -> list:
        return [("target", self.target), ("value", self.value)]


class IfStmt(ASTNode):
    """if (condition) then_block [else else_block]"""

    def __init__(self, condition: ASTNode, then_block: Block,
                 else_block: Optional[Block] = None,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def node_children(self) -> list:
        children: list = [("condition", self.condition),
                          ("then", self.then_block)]
        if self.else_block:
            children.append(("else", self.else_block))
        return children


class ForStmt(ASTNode):
    """for (init; condition; update) body"""

    def __init__(self, init: ASTNode, condition: ASTNode,
                 update: ASTNode, body: Block,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def node_children(self) -> list:
        return [("init", self.init), ("condition", self.condition),
                ("update", self.update), ("body", self.body)]


class DoWhileStmt(ASTNode):
    """do { body } while (condition) ;"""

    def __init__(self, body: Block, condition: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.body = body
        self.condition = condition

    def node_children(self) -> list:
        return [("body", self.body), ("condition", self.condition)]


class ReturnStmt(ASTNode):
    """return expr ;"""

    def __init__(self, value: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def node_children(self) -> list:
        return [("value", self.value)]


class PrintStmt(ASTNode):
    """print(expr) ;  — built-in I/O subprogram, NOT an operator."""

    def __init__(self, value: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def node_children(self) -> list:
        return [("value", self.value)]


class ExprStmt(ASTNode):
    """An expression used as a statement (e.g. function call)."""

    def __init__(self, expr: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expr = expr

    def node_children(self) -> list:
        return [("expr", self.expr)]


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

class BinaryOp(ASTNode):
    """Binary operation: left op right"""

    def __init__(self, op: str, left: ASTNode, right: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.op = op
        self.left = left
        self.right = right

    def node_attrs(self) -> dict:
        return {"op": self.op}

    def node_children(self) -> list:
        return [("left", self.left), ("right", self.right)]


class IntLiteral(ASTNode):
    def __init__(self, value: int, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def node_attrs(self) -> dict:
        return {"value": self.value}


class FloatLiteral(ASTNode):
    def __init__(self, value: float, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def node_attrs(self) -> dict:
        return {"value": self.value}


class StringLiteral(ASTNode):
    def __init__(self, value: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def node_attrs(self) -> dict:
        return {"value": repr(self.value)}


class Identifier(ASTNode):
    def __init__(self, name: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name

    def node_attrs(self) -> dict:
        return {"name": self.name}


class ArrayLiteral(ASTNode):
    """[expr, expr, ...]"""

    def __init__(self, elements: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.elements = elements

    def node_children(self) -> list:
        return [("elements", self.elements)]


class ArrayAccess(ASTNode):
    """array[index]"""

    def __init__(self, array: ASTNode, index: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.array = array
        self.index = index

    def node_children(self) -> list:
        return [("array", self.array), ("index", self.index)]


class MemberAccess(ASTNode):
    """object.member"""

    def __init__(self, obj: ASTNode, member: str,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.object = obj
        self.member = member

    def node_attrs(self) -> dict:
        return {"member": self.member}

    def node_children(self) -> list:
        return [("object", self.object)]


class FunctionCall(ASTNode):
    """callee(args)"""

    def __init__(self, callee: ASTNode, args: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.callee = callee
        self.args = args

    def node_children(self) -> list:
        return [("callee", self.callee), ("args", self.args)]


class MethodCall(ASTNode):
    """object.method(args)"""

    def __init__(self, obj: ASTNode, method: str,
                 args: List[ASTNode],
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.object = obj
        self.method = method
        self.args = args

    def node_attrs(self) -> dict:
        return {"method": self.method}

    def node_children(self) -> list:
        return [("object", self.object), ("args", self.args)]


class NewObject(ASTNode):
    """new ClassName()"""

    def __init__(self, class_name: str,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.class_name = class_name

    def node_attrs(self) -> dict:
        return {"class": self.class_name}


class NewStack(ASTNode):
    """new Stack()  — element type inferred from declaration context."""

    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)

    def node_attrs(self) -> dict:
        return {}


class ThisExpr(ASTNode):
    """The 'this' keyword — refers to the current object inside a method."""

    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)


# ---------------------------------------------------------------------------
# AST pretty-printer
# ---------------------------------------------------------------------------

def format_ast(node: Any, indent: int = 0) -> str:
    """
    Recursively format an AST node (and its children) as an indented tree.
    Used by the --ast CLI flag.
    """
    prefix = "  " * indent

    if node is None:
        return ""

    # Handle bare lists (e.g. a list of statements)
    if isinstance(node, list):
        return "".join(format_ast(item, indent) for item in node)

    if not isinstance(node, ASTNode):
        return f"{prefix}{node}\n"

    # Node header: ClassName(attr=val, attr=val)
    attrs = node.node_attrs()
    attr_str = ", ".join(f"{k}={v}" for k, v in attrs.items())
    header = f"{node.node_name()}({attr_str})" if attr_str else node.node_name()
    result = f"{prefix}{header}\n"

    # Children
    for label, child in node.node_children():
        if isinstance(child, list):
            if child:
                result += f"{prefix}  {label}:\n"
                for item in child:
                    result += format_ast(item, indent + 2)
        elif isinstance(child, ASTNode):
            result += f"{prefix}  {label}:\n"
            result += format_ast(child, indent + 2)
        elif child is not None:
            result += f"{prefix}  {label}: {child}\n"

    return result

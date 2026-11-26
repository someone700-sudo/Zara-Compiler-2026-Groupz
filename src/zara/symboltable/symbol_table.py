"""
Symbol table for the Zara compiler (Week 1).

WHY: The symbol table maps names to their declarations so that the semantic
analyzer can check types, the TAC generator can resolve variables, and the
code generator can allocate storage.  Scopes are stacked: entering a function,
method, or class pushes a new scope; leaving pops it.  Lookup walks from the
innermost scope outward, implementing lexical scoping.

Operations: add (insert, detect duplicates), update, search/lookup, retrieve.
"""

from typing import Optional, List, Dict, Any


class SymbolInfo:
    """
    Information stored for each symbol in the table.

    kind          : 'variable', 'function', 'class', 'method', 'field', 'parameter'
    data_type     : type string, e.g. 'Integer', 'Array<Float>', 'Dog'
    scope_level   : nesting depth (0 = global)
    element_type  : for Array / Stack — the inner type, e.g. 'Integer'
    return_type   : for function / method
    params        : list of (name, type_str) for function / method
    parent_class  : for class — name of the superclass, or None
    members       : for class — dict of member name -> SymbolInfo
    """

    def __init__(self, name: str, kind: str, data_type: str,
                 scope_level: int = 0, line: int = 0, col: int = 0,
                 element_type: Optional[str] = None,
                 size: Optional[int] = None,
                 return_type: Optional[str] = None,
                 params: Optional[List] = None,
                 parent_class: Optional[str] = None,
                 members: Optional[Dict[str, "SymbolInfo"]] = None):
        self.name = name
        self.kind = kind
        self.data_type = data_type
        self.scope_level = scope_level
        self.line = line
        self.col = col
        self.element_type = element_type
        self.size = size
        self.return_type = return_type
        self.params = params if params is not None else []
        self.parent_class = parent_class
        self.members = members if members is not None else {}

    def __repr__(self) -> str:
        parts = [f"name={self.name!r}", f"kind={self.kind!r}",
                 f"type={self.data_type!r}", f"scope={self.scope_level}"]
        if self.element_type:
            parts.append(f"elem={self.element_type!r}")
        if self.size is not None:
            parts.append(f"size={self.size}")
        if self.return_type:
            parts.append(f"ret={self.return_type!r}")
        if self.params:
            parts.append(f"params={self.params!r}")
        if self.parent_class:
            parts.append(f"parent={self.parent_class!r}")
        return f"SymbolInfo({', '.join(parts)})"


class SymbolTable:
    """
    Scoped symbol table using a stack of dictionaries.

    Each scope is a dict mapping names to SymbolInfo objects.  `enter_scope`
    pushes a fresh dict; `exit_scope` pops it.  `lookup` walks from the
    innermost scope outward so inner names shadow outer ones.
    """

    def __init__(self):
        self._scopes: List[Dict[str, SymbolInfo]] = [{}]  # start with global
        self.scope_level: int = 0
        self._all_symbols: List[SymbolInfo] = []  # flat log for dumping

    # ---- Scope management ----

    def enter_scope(self) -> None:
        """Push a new scope."""
        self.scope_level += 1
        self._scopes.append({})

    def exit_scope(self) -> None:
        """Pop the innermost scope."""
        self._scopes.pop()
        self.scope_level -= 1

    def current_scope_level(self) -> int:
        return self.scope_level

    # ---- Core operations ----

    def add(self, name: str, info: SymbolInfo) -> bool:
        """
        Add a symbol to the current scope.
        Returns False if the name already exists in the CURRENT scope
        (redeclaration error).  Duplicate names in outer scopes are OK
        (shadowing).
        """
        current = self._scopes[-1]
        if name in current:
            return False
        info.scope_level = self.scope_level
        current[name] = info
        self._all_symbols.append(info)
        return True

    def update(self, name: str, info: SymbolInfo) -> bool:
        """
        Update an existing symbol (found by walking scopes outward).
        Returns False if the name is not found anywhere.
        """
        for scope in reversed(self._scopes):
            if name in scope:
                info.scope_level = scope[name].scope_level
                scope[name] = info
                return True
        return False

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Look up a name from the innermost scope outward (lexical scoping)."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> Optional[SymbolInfo]:
        """Look up a name only in the current (innermost) scope."""
        return self._scopes[-1].get(name)

    def search(self, name: str) -> bool:
        """Check whether a name exists anywhere in scope."""
        return self.lookup(name) is not None

    def retrieve(self, name: str) -> Optional[SymbolInfo]:
        """Alias for lookup (required by the assignment spec)."""
        return self.lookup(name)

    # ---- Formatting ----

    def format_table(self) -> str:
        """Format the full symbol table for display (--symbols flag)."""
        header = (f"{'Name':<20} {'Kind':<12} {'Type':<20} "
                  f"{'Scope':<6} {'Extra'}")
        sep = "-" * 80
        lines = ["\n" + sep, "  SYMBOL TABLE", sep, header, sep]
        for sym in self._all_symbols:
            extra_parts: list = []
            if sym.element_type:
                extra_parts.append(f"elem={sym.element_type}")
            if sym.size is not None:
                extra_parts.append(f"size={sym.size}")
            if sym.return_type:
                extra_parts.append(f"ret={sym.return_type}")
            if sym.params:
                param_str = ", ".join(f"{n}:{t}" for n, t in sym.params)
                extra_parts.append(f"params=({param_str})")
            if sym.parent_class:
                extra_parts.append(f"extends {sym.parent_class}")
            if sym.members:
                extra_parts.append(f"members=[{', '.join(sym.members)}]")
            extra = "; ".join(extra_parts) if extra_parts else ""
            lines.append(
                f"{sym.name:<20} {sym.kind:<12} {sym.data_type:<20} "
                f"{sym.scope_level:<6} {extra}")
        lines.append(sep)
        return "\n".join(lines)

    def format_scopes(self) -> str:
        """Show current scope stack (debugging helper)."""
        lines: list = []
        for i, scope in enumerate(self._scopes):
            names = ", ".join(scope.keys()) if scope else "(empty)"
            lines.append(f"  Scope {i}: {names}")
        return "\n".join(lines)


def demo_symbol_table() -> None:
    """
    Standalone demo for --demo-symbols.
    Builds a symbol table programmatically from a sample set of Zara
    declarations, including duplicates and missing lookups, then prints it.
    """
    st = SymbolTable()
    print("=" * 60)
    print("  SYMBOL TABLE DEMO")
    print("=" * 60)

    # --- Global scope ---
    print("\n--- Adding global declarations ---")

    syms = [
        SymbolInfo("x", "variable", "Integer", line=1, col=1),
        SymbolInfo("pi", "variable", "Float", line=2, col=1),
        SymbolInfo("greeting", "variable", "String", line=3, col=1),
        SymbolInfo("nums", "variable", "Array<Integer>", line=4, col=1,
                   element_type="Integer", size=5),
        SymbolInfo("stk", "variable", "Stack<Integer>", line=5, col=1,
                   element_type="Integer"),
        SymbolInfo("mul", "function", "function", line=7, col=1,
                   return_type="Integer",
                   params=[("a", "Integer"), ("b", "Integer")]),
    ]
    for s in syms:
        ok = st.add(s.name, s)
        status = "OK" if ok else "DUPLICATE"
        print(f"  add({s.name:12s}, {s.kind:10s}, {s.data_type:18s}) -> {status}")

    # Duplicate test
    dup = SymbolInfo("x", "variable", "Float", line=10, col=1)
    ok = st.add("x", dup)
    print(f"  add({'x':12s}, {'variable':10s}, {'Float':18s}) -> "
          f"{'OK' if ok else 'DUPLICATE (expected)'}")

    # --- Function scope ---
    print("\n--- Entering function 'mul' scope ---")
    st.enter_scope()
    for name, typ in [("a", "Integer"), ("b", "Integer")]:
        p = SymbolInfo(name, "parameter", typ, line=7, col=20)
        st.add(name, p)
        print(f"  add({name:12s}, parameter, {typ})")
    result = SymbolInfo("result", "variable", "Integer", line=8, col=5)
    st.add("result", result)
    print(f"  add(result      , variable , Integer)")

    # --- Lookups ---
    print("\n--- Lookups from inside function scope ---")
    for name in ["a", "result", "x", "greeting", "unknown"]:
        found = st.lookup(name)
        if found:
            print(f"  lookup({name:12s}) -> {found.kind}, {found.data_type}, "
                  f"scope {found.scope_level}")
        else:
            print(f"  lookup({name:12s}) -> NOT FOUND")

    st.exit_scope()
    print("\n--- After exiting function scope ---")
    for name in ["a", "x"]:
        found = st.lookup(name)
        if found:
            print(f"  lookup({name:12s}) -> {found.kind}, {found.data_type}, "
                  f"scope {found.scope_level}")
        else:
            print(f"  lookup({name:12s}) -> NOT FOUND (expected — out of scope)")

    # --- Class scope ---
    print("\n--- Adding class 'Animal' ---")
    cls = SymbolInfo("Animal", "class", "Animal", line=12, col=1)
    cls.members = {
        "age": SymbolInfo("age", "field", "Integer"),
        "speak": SymbolInfo("speak", "method", "method",
                            return_type="Integer", params=[]),
    }
    st.add("Animal", cls)
    print(f"  add(Animal, class, members=[age, speak])")

    dog_cls = SymbolInfo("Dog", "class", "Dog", line=18, col=1,
                         parent_class="Animal")
    dog_cls.members = {
        "speak": SymbolInfo("speak", "method", "method",
                            return_type="Integer", params=[]),
    }
    st.add("Dog", dog_cls)
    print(f"  add(Dog, class, extends Animal, members=[speak])")

    # --- Update ---
    print("\n--- Update x to Integer value 99 ---")
    updated = SymbolInfo("x", "variable", "Integer", line=1, col=1)
    ok = st.update("x", updated)
    print(f"  update(x) -> {'OK' if ok else 'NOT FOUND'}")

    ok = st.update("nonexistent", SymbolInfo("nonexistent", "variable", "Integer"))
    print(f"  update(nonexistent) -> {'OK' if ok else 'NOT FOUND (expected)'}")

    # --- Full table ---
    print(st.format_table())
    print("\n--- Demo complete ---")

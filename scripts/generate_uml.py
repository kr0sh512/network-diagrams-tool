#!/usr/bin/env python3
"""
Auto-generate a D2 UML class diagram from a Python source file using AST parsing.

Usage:
    python scripts/generate_uml.py [input.py] [output.d2]

Defaults:
    input  → src/netdiag/domain/models.py
    output → UML/UML.d2
"""

import ast
import sys
from pathlib import Path

# ── helpers ───


def _unparse(node: ast.expr) -> str:
    """Return a clean string for an AST annotation, stripping forward-ref quotes."""
    return ast.unparse(node).strip("'\"")


def _d2_quote(s: str) -> str:
    """
    Wrap *s* in D2 double-quotes only when it contains characters that the D2
    parser would otherwise misinterpret (colons inside arg lists, brackets, …).
    """
    needs_quoting = any(c in s for c in '():[],<> "')
    return f'"{s}"' if needs_quoting else s


# ── parsing ──


def parse_classes(source: str) -> list[dict]:
    """
    Walk the top-level statements of *source* and return one dict per class:

        {
            "name":    str,
            "bases":   list[str],          # base-class names
            "attrs":   list[(name, type)], # class-level annotated attributes
            "methods": list[(name, args_str, return_str)],
        }
    """
    tree = ast.parse(source)
    classes: list[dict] = []

    for node in tree.body:  # top-level only – no nested classes
        if not isinstance(node, ast.ClassDef):
            continue

        bases = [_unparse(b) for b in node.bases]
        attrs: list[tuple[str, str]] = []
        methods: list[tuple[str, str, str]] = []

        for item in node.body:

            # ── class-level type annotation ───
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attrs.append((_unparse(item.target), _unparse(item.annotation)))

            # ── method definition ───
            elif isinstance(item, ast.FunctionDef):
                # Build the argument string, skipping 'self'
                func_args: list[str] = []
                for arg in item.args.args:
                    if arg.arg == "self":
                        continue
                    if arg.annotation:
                        func_args.append(f"{arg.arg}: {_unparse(arg.annotation)}")
                    else:
                        func_args.append(arg.arg)

                # Mark arguments that have defaults as [optional]
                n_required = len(func_args) - len(item.args.defaults)
                for i in range(n_required, len(func_args)):
                    func_args[i] = f"[{func_args[i]}]"

                args_str = ", ".join(func_args)
                ret_str = _unparse(item.returns) if item.returns else ""
                methods.append((item.name, args_str, ret_str))

        classes.append(
            {"name": node.name, "bases": bases, "attrs": attrs, "methods": methods}
        )

    return classes


# ── relationship detection ───


def detect_associations(classes: list[dict]) -> list[tuple[str, str, str, str]]:
    """
    Detect associations between classes by scanning type annotations for
    references to other known class names.

    Returns a list of (src, dst, label, multiplicity) where multiplicity is
    "many" (Dict / List) or "one".

    When the same class pair appears with both a "many" and a "one" reference
    (e.g. Device.interfaces and Interface.device), the "many" side wins so the
    diagram shows the semantically richer direction.
    """
    all_names: set[str] = {c["name"] for c in classes}

    # Keyed by the canonical (alphabetically sorted) class pair so that A→B
    # and B→A collapse into a single relationship.
    raw: dict[tuple[str, str], tuple[str, str, str, str]] = {}

    for c in classes:
        src = c["name"]
        for attr_name, attr_type in c["attrs"]:
            for other in all_names:
                if other == src:
                    continue
                if other not in attr_type:
                    continue

                many = any(kw in attr_type for kw in ("Dict", "List"))
                mult = "many" if many else "one"

                key = tuple(sorted([src, other]))
                existing = raw.get(key)  # type: ignore[assignment]

                # Always prefer the "many" direction; only add "one" if nothing
                # has been recorded yet for this pair.
                if existing is None or (mult == "many" and existing[3] == "one"):
                    raw[key] = (src, other, attr_name, mult)  # type: ignore[assignment]

    return list(raw.values())  # type: ignore[return-value]


# ── D2 rendering ───

_INHERIT = """\
{child} -> {parent}: {{
  target-arrowhead.shape: triangle
  target-arrowhead.style.filled: false
}}"""

_ASSOC_MANY = """\
{src} -- {dst}: {label} {{
  source-arrowhead: 1..*
  target-arrowhead: 1
}}"""

_ASSOC_ONE = """\
{src} -- {dst}: {label} {{
  source-arrowhead: 1
  target-arrowhead: 1
}}"""


def to_d2(classes: list[dict]) -> str:
    all_names = {c["name"] for c in classes}
    lines: list[str] = ["direction: down", ""]

    # ── class blocks ───
    for c in classes:
        lines.append(f"{c['name']}: {{")
        lines.append("  shape: class")

        if c["attrs"]:
            lines.append("")
            for name, typ in c["attrs"]:
                lines.append(f"  {name}: {_d2_quote(typ)}")

        if c["methods"]:
            lines.append("")
            for mname, args, ret in c["methods"]:
                sig = f"{mname}({args})"
                if ret:
                    sig += f": {ret}"
                lines.append(f"  {_d2_quote(sig)}")

        lines += ["}", ""]

    # ── inheritance arrows ───
    for c in classes:
        for base in c["bases"]:
            if base in all_names:
                lines.append(_INHERIT.format(child=c["name"], parent=base))
                lines.append("")

    # ── association edges ───
    for src, dst, label, mult in detect_associations(classes):
        tmpl = _ASSOC_MANY if mult == "many" else _ASSOC_ONE
        lines.append(tmpl.format(src=src, dst=dst, label=label))
        lines.append("")

    return "\n".join(lines)


# ── entry point ───


def main() -> None:
    models_path = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/netdiag/domain/models.py")
    )
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("UML/UML.d2")

    if not models_path.exists():
        sys.exit(f"Error: {models_path} not found")

    source = models_path.read_text()
    classes = parse_classes(source)
    d2_content = to_d2(classes)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(d2_content)
    print(f"Generated {output_path} ({len(classes)} classes)")


if __name__ == "__main__":
    main()

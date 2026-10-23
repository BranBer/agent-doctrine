"""Prints every import cycle between a Python project's own modules.

    python pycycles.py <dir>

Resolves absolute imports of the project's modules and relative imports by
their level. Exits 1 when there is a cycle. ruff has no cycle rule, which is
why this exists.
"""

import ast
import sys
from pathlib import Path

SKIP = {".venv", "venv", "env", "__pycache__", "node_modules", ".git", "build", "dist", ".tox"}


def module_name(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def is_type_checking(node: ast.AST) -> bool:
    test = getattr(node, "test", None)
    return isinstance(node, ast.If) and (
        (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING")
        or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
    )


def runtime_nodes(tree: ast.AST):
    """Every node except those under `if TYPE_CHECKING:`, which never run."""
    stack = [tree]
    while stack:
        node = stack.pop()
        yield node
        if is_type_checking(node):
            stack.extend(node.orelse)
            continue
        stack.extend(ast.iter_child_nodes(node))


def imports_of(path: Path, name: str, known: set[str]) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    package = name if path.name == "__init__.py" else name.rpartition(".")[0]
    found: set[str] = set()
    for node in runtime_nodes(tree):
        if isinstance(node, ast.Import):
            targets = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parent = package.split(".") if package else []
                parent = parent[: len(parent) - (node.level - 1)] if node.level > 1 else parent
                base = ".".join([*parent, base] if base else parent)
            # `from pkg import sub` imports the module pkg.sub when there is one,
            # and only otherwise a name from pkg's __init__.
            full = [f"{base}.{alias.name}" if base else alias.name for alias in node.names]
            targets = [t for t in full if t in known] or [base]
        else:
            continue
        for target in targets:
            while target and target not in known:
                target = target.rpartition(".")[0]
            if target and target != name:
                found.add(target)
    return found


def cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    result: list[list[str]] = []
    counter = [0]

    def visit(node: str) -> None:
        index[node] = low[node] = counter[0]
        counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph.get(node, ()):
            if nxt not in index:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in on_stack:
                low[node] = min(low[node], index[nxt])
        if low[node] == index[node]:
            group = []
            while True:
                top = stack.pop()
                on_stack.discard(top)
                group.append(top)
                if top == node:
                    break
            if len(group) > 1:
                result.append(sorted(group))

    sys.setrecursionlimit(10_000)
    for node in graph:
        if node not in index:
            visit(node)
    return result


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = [p for p in root.rglob("*.py") if not SKIP.intersection(p.relative_to(root).parts)]
    # In a src/ layout the package is imported as `app`, not `src.app`.
    base = root / "src" if (root / "src").is_dir() else root
    names = {module_name(p, base if base in p.parents else root): p for p in files}
    known = set(names)
    graph = {name: imports_of(path, name, known) for name, path in names.items()}
    found = cycles(graph)
    for group in found:
        print("cycle: " + " -> ".join(group))
    print(f"{len(found)} import cycle(s)" if found else "no import cycles")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

"""Syntax check all Python source files."""
import ast
from pathlib import Path

root = Path(".")
errors = []
ok = []
for p in sorted(root.rglob("*.py")):
    if "__pycache__" in str(p) or "extract_" in str(p):
        continue
    try:
        ast.parse(p.read_text(encoding="utf-8"))
        ok.append(p)
    except SyntaxError as e:
        errors.append((p, e))

print(f"OK: {len(ok)} files")
if errors:
    print(f"\nERRORS: {len(errors)}")
    for p, e in errors:
        print(f"  {p}: {e}")
else:
    print("All files syntax-clean.")

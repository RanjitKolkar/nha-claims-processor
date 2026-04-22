import importlib, sys

REQUIRED = [
    ("fitz", "pymupdf"),
    ("cv2", "opencv-python"),
    ("pytesseract", "pytesseract"),
    ("PIL", "Pillow"),
    ("pydantic", "pydantic"),
    ("yaml", "PyYAML"),
    ("tqdm", "tqdm"),
    ("sklearn", "scikit-learn"),
    ("numpy", "numpy"),
    ("dateutil", "python-dateutil"),
    ("pandas", "pandas"),
]

missing = []
for mod, pkg in REQUIRED:
    try:
        importlib.import_module(mod)
        print(f"  OK  {pkg}")
    except ImportError:
        print(f"  MISSING  {pkg}")
        missing.append(pkg)

if missing:
    print(f"\nInstall missing: pip install {' '.join(missing)}")
else:
    print("\nAll dependencies satisfied.")

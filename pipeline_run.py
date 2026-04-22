"""CLI wrapper so the Streamlit UI can invoke the pipeline as a subprocess."""
import argparse
import sys
import io
from pathlib import Path

# Force UTF-8 output so Unicode emoji in report_generator don't crash on cp1252
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim_dir",    required=True)
    parser.add_argument("--package_code", required=True)
    args = parser.parse_args()

    claim_dir    = Path(args.claim_dir)
    package_code = args.package_code

    if not claim_dir.exists():
        print(f"ERROR: claim_dir not found: {claim_dir}", file=sys.stderr)
        sys.exit(1)

    from pipeline import ClaimProcessor
    pipe = ClaimProcessor()
    result = pipe.process(claim_dir, package_code)
    print(f"Done: {result.claim_id} → {result.verdict}")

if __name__ == "__main__":
    main()

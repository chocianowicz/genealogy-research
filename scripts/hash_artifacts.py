#!/usr/bin/env python3
"""Hash saved artifacts (scans, PDFs, pages) with SHA-256.

Usage:
  python3 hash_artifacts.py <file_or_dir> [...]          print "sha256  size  path"
  python3 hash_artifacts.py --write <dir> [...]          also write/update <dir>/SHA256SUMS
  python3 hash_artifacts.py --check <dir>                verify files against <dir>/SHA256SUMS

Hidden files and SHA256SUMS itself are skipped.
"""
import hashlib
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files(target: Path):
    if target.is_file():
        yield target
        return
    for p in sorted(target.rglob("*")):
        if p.is_file() and not p.name.startswith(".") and p.name != "SHA256SUMS":
            yield p


def main(argv) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--check":
        d = Path(argv[1])
        sums = d / "SHA256SUMS"
        bad = 0
        for line in sums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            p = d / rel
            if not p.exists():
                print(f"MISSING  {rel}")
                bad += 1
            elif sha256(p) != digest:
                print(f"CHANGED  {rel}")
                bad += 1
        print("OK" if not bad else f"{bad} problem(s)")
        return 1 if bad else 0
    write = argv[0] == "--write"
    targets = [Path(a) for a in (argv[1:] if write else argv)]
    for t in targets:
        lines = []
        for p in files(t):
            digest = sha256(p)
            print(f"{digest}  {p.stat().st_size:>10}  {p}")
            if write and t.is_dir():
                lines.append(f"{digest}  {p.relative_to(t)}")
        if write and t.is_dir():
            (t / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"written {t / 'SHA256SUMS'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

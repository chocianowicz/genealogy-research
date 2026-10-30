#!/usr/bin/env python3
"""Verify scans downloaded from epaveldas.lt and identify renamed/hidden downloads.

epaveldas original page files are named NNNN-<MD5>.jpg, where <MD5> is the MD5 of the file.

Usage:
  python3 verify_epaveldas_md5.py <file_or_dir> [...]
      Checks every NNNN-<MD5>.jpg name against its content.
  python3 verify_epaveldas_md5.py --match <known_names.txt> <dir>
      known_names.txt holds the original names (one per line, e.g. copied from the browser network log);
      prints which local file (any name, incl. hidden temp files) matches which page.
"""
import hashlib
import re
import sys
from pathlib import Path

PAT = re.compile(r"^(\d{4})-([0-9A-Fa-f]{32})\.jpe?g$")


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def iter_files(t: Path):
    if t.is_file():
        yield t
    else:
        for p in sorted(t.iterdir()):
            if p.is_file():
                yield p


def main(argv) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--match":
        names = [n.strip() for n in Path(argv[1]).read_text().splitlines() if n.strip()]
        want = {}
        for n in names:
            m = PAT.match(Path(n).name)
            if m:
                want[m.group(2).lower()] = m.group(1)
        found = {}
        for p in iter_files(Path(argv[2])):
            d = md5(p)
            if d in want:
                found[want[d]] = p
        for page in sorted(want.values()):
            print(f"page {page}: {found.get(page, 'NOT FOUND')}")
        return 0 if len(found) == len(want) else 1
    bad = 0
    for a in argv:
        for p in iter_files(Path(a)):
            m = PAT.match(p.name)
            if not m:
                continue
            ok = md5(p) == m.group(2).lower()
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'}  {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

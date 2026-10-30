#!/usr/bin/env python3
"""Scan the repository for private data before it is published.

Usage:
  python3 privacy_audit.py [--history] [--denylist FILE] [--allow-no-denylist]

Checks every text file in the repo (tracked files if it is a git checkout, otherwise all files) for:
  - terms from a private denylist (one term per line, '#' comments, case-insensitive)
  - generic personal-data patterns: e-mail addresses, phone numbers, PESEL-like 11-digit numbers
With --history it also scans every commit reachable from any ref (added lines only).

The denylist lives outside version control: <repo>/.private/anonymization-denylist.txt (git-ignored).
Put real surnames, villages and given names of your family in it. Matches are reported as
file:line and the matched term only; the surrounding line is never printed.

Exit code: 0 clean, 1 findings, 2 setup problem (no denylist).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DENYLIST = ROOT / ".private" / "anonymization-denylist.txt"
SKIP_DIRS = {".git", "__pycache__", ".private", "cases"}
# lines in these files may legitimately show the patterns (this script and CI config)
SKIP_PATTERN_FILES = {"scripts/privacy_audit.py"}

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<!\d)(?:\+|00)\d{1,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3}[\s-]?\d{2,4}[\s-]?\d{0,4}(?!\d)"),
    "pesel-like": re.compile(r"(?<!\d)\d{11}(?!\d)"),
}
# well-known placeholder addresses that are fine in docs
ALLOWED_EMAILS = {"noreply@anthropic.com", "user@example.com", "name@example.com"}


def load_terms(path, required):
    if not path.exists():
        if required:
            print(f"Missing denylist: {path}\nCreate it (one private term per line) or pass --allow-no-denylist.",
                  file=sys.stderr)
            sys.exit(2)
        return []
    terms = [t.strip() for t in path.read_text(encoding="utf-8").splitlines()]
    return [t for t in terms if t and not t.startswith("#")]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, errors="replace")


def repo_files():
    res = git("ls-files")
    if res.returncode == 0 and res.stdout.strip():
        names = res.stdout.splitlines()
    else:
        names = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()]
    out = []
    for name in names:
        p = ROOT / name
        if set(p.relative_to(ROOT).parts) & SKIP_DIRS or not p.is_file():
            continue
        try:
            if b"\x00" in p.read_bytes()[:2048]:
                continue
        except OSError:
            continue
        out.append(name)
    return out


def scan_line(name, lineno, line, terms, findings):
    low = line.lower()
    for term in terms:
        if term.lower() in low:
            findings.append((name, lineno, f"denylist term '{term}'"))
    if name in SKIP_PATTERN_FILES:
        return
    for label, rx in PATTERNS.items():
        for m in rx.finditer(line):
            if label == "email" and m.group(0).lower() in ALLOWED_EMAILS:
                continue
            findings.append((name, lineno, f"{label} pattern"))


def scan_working_tree(terms):
    findings = []
    for name in repo_files():
        text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            scan_line(name, i, line, terms, findings)
    return findings


def scan_history(terms):
    findings = []
    res = git("log", "--all", "-p", "--no-color", "--format=commit %h", "--unified=0")
    if res.returncode != 0:
        print("git log failed; is this a git checkout?", file=sys.stderr)
        return findings
    commit, current = "?", "?"
    for line in res.stdout.splitlines():
        if line.startswith("commit "):
            commit = line.split()[1]
        elif line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            scan_line(f"{current}@{commit}", 0, line[1:], terms, findings)
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--history", action="store_true", help="also scan added lines in all commits")
    ap.add_argument("--denylist", type=Path, default=DEFAULT_DENYLIST)
    ap.add_argument("--allow-no-denylist", action="store_true",
                    help="run only the generic patterns (use in CI where the private list is unavailable)")
    args = ap.parse_args()

    terms = load_terms(args.denylist, required=not args.allow_no_denylist)
    findings = scan_working_tree(terms)
    if args.history:
        findings += scan_history(terms)

    if not terms:
        print("note: no denylist loaded; only generic patterns were checked")
    for name, lineno, what in sorted(set(findings)):
        where = f"{name}:{lineno}" if lineno else name
        print(f"{where}: {what}")
    print(f"{len(set(findings))} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

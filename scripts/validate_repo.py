#!/usr/bin/env python3
"""Validate the structure of this repository.

Usage: python3 validate_repo.py

Checks:
  - SKILL.md has frontmatter with name and description
  - every agents/*.md has frontmatter whose name matches the file name, plus a description
  - every template, reference and script named in README.md and SKILL.md exists
  - relative Markdown links resolve
  - every script compiles and has a usage docstring
  - evals/scenarios.yaml cases each have id, prompt and expect
  - install.sh copies only paths that exist
  - SKILL.md keeps the hard-rule section and the living-people rule

Exit code: 0 ok, 1 problems found.
"""
import py_compile
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems = []


def fail(msg):
    problems.append(msg)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def check_skill():
    fm = frontmatter(ROOT / "SKILL.md")
    if fm is None:
        fail("SKILL.md: missing frontmatter")
        return
    for key in ("name", "description"):
        if not fm.get(key):
            fail(f"SKILL.md: frontmatter lacks '{key}'")
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "Hard rules" not in text:
        fail("SKILL.md: hard-rules section missing")
    if "Living people" not in text:
        fail("SKILL.md: living-people rule missing")


def check_agents():
    for path in sorted((ROOT / "agents").glob("*.md")):
        fm = frontmatter(path)
        if fm is None:
            fail(f"{path.relative_to(ROOT)}: missing frontmatter")
            continue
        if fm.get("name") != path.stem:
            fail(f"{path.relative_to(ROOT)}: name '{fm.get('name')}' does not match file name")
        if not fm.get("description"):
            fail(f"{path.relative_to(ROOT)}: missing description")


def check_mentioned_paths():
    rx = re.compile(r"`((?:references|templates|scripts|agents)/[A-Za-z0-9_./-]+\.[a-z]+)`")
    for doc in ("README.md", "SKILL.md"):
        for ref in sorted(set(rx.findall((ROOT / doc).read_text(encoding="utf-8")))):
            if not (ROOT / ref).exists():
                fail(f"{doc}: mentions missing file {ref}")


def check_links():
    rx = re.compile(r"\]\((?!https?:|mailto:|#)([^)#\s]+)")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in rx.findall(path.read_text(encoding="utf-8")):
            if not (path.parent / target).exists():
                fail(f"{path.relative_to(ROOT)}: broken link {target}")


def check_scripts():
    for path in sorted((ROOT / "scripts").glob("*.py")):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                py_compile.compile(str(path), cfile=str(Path(tmp) / "x.pyc"), doraise=True)
        except py_compile.PyCompileError as exc:
            fail(f"{path.relative_to(ROOT)}: does not compile ({exc.msg.strip()})")
        if "Usage" not in path.read_text(encoding="utf-8")[:1500]:
            fail(f"{path.relative_to(ROOT)}: no usage docstring")


def check_evals():
    text = (ROOT / "evals" / "scenarios.yaml").read_text(encoding="utf-8")
    cases = re.split(r"(?m)^- ", text)[1:]
    if not cases:
        fail("evals/scenarios.yaml: no cases")
    seen = set()
    for case in cases:
        m = re.match(r"id:\s*(\S+)", case)
        if not m:
            fail("evals/scenarios.yaml: case without id")
            continue
        cid = m.group(1)
        if cid in seen:
            fail(f"evals/scenarios.yaml: duplicate id {cid}")
        seen.add(cid)
        for key in ("prompt:", "expect:"):
            if key not in case:
                fail(f"evals/scenarios.yaml: case {cid} lacks {key[:-1]}")


def check_install():
    text = (ROOT / "install.sh").read_text(encoding="utf-8")
    for name in re.findall(r'"\$SRC/([A-Za-z0-9_.]+)"', text):
        if not (ROOT / name).exists():
            fail(f"install.sh: copies missing path {name}")
    if "$SRC/agents" in text and not list((ROOT / "agents").glob("*.md")):
        fail("install.sh: no agents to copy")


def main():
    for check in (check_skill, check_agents, check_mentioned_paths, check_links,
                  check_scripts, check_evals, check_install):
        check()
    for p in problems:
        print(f"FAIL {p}")
    print(f"{len(problems)} problem(s)" if problems else "ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

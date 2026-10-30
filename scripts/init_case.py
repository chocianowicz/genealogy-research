#!/usr/bin/env python3
"""Create a genealogy case folder with registers and templates.

Usage: python3 init_case.py <case_dir>
Existing files are never overwritten.
"""
import shutil
import sys
from pathlib import Path

HEADERS = {
    "persons.csv": "person_id,names_as_written,normalized_name,sex,birth,death,place_ids,social_estate,confession,notes",
    "places.csv": "place_id,names,coords,jurisdictions_by_date,parishes,owners_by_date,notes",
    "artifacts.csv": "artifact_id,title,repository,shelfmark,url,doc_date,kind,language,independence_group,file,sha256,read_quality,accessed,notes",
    "claims.csv": "claim_id,statement,artifact_ids,independence_groups,status,kind,notes",
    "relationships.csv": "rel_id,person_a,relation,person_b,claim_ids,status,notes",
    "search_log.csv": "date,resource,query,scope,result,artifact_ids,next",
}
DIRS = ["registers", "places", "persons", "media", "sources", "reports"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    case = Path(sys.argv[1]).expanduser()
    for d in DIRS:
        (case / d).mkdir(parents=True, exist_ok=True)
    for name, header in HEADERS.items():
        p = case / "registers" / name
        if not p.exists():
            p.write_text(header + "\n", encoding="utf-8")
    templates = Path(__file__).resolve().parent.parent / "templates"
    for src, dst in [("intake.md", "intake.md"), ("links_to_try_later.md", "links_to_try_later.md")]:
        target = case / dst
        if not target.exists() and (templates / src).exists():
            shutil.copy(templates / src, target)
    print(f"Case ready: {case}")
    for p in sorted(case.rglob("*")):
        print("  ", p.relative_to(case))
    return 0


if __name__ == "__main__":
    sys.exit(main())

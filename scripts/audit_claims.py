#!/usr/bin/env python3
"""Audit a genealogy case: referential integrity and evidence strength.

Usage: python3 audit_claims.py <case_dir>

Checks registers/claims.csv, artifacts.csv, relationships.csv, persons.csv:
  - unknown artifact / claim / person IDs
  - claim status stronger than its independence groups allow
  - corroboration built only from copies of one record (one independence group)
  - 'strongly-corroborated' without any original record
  - relationships graded stronger than any of their supporting claims
  - artifacts without repository/shelfmark/url, read only provisionally, or missing files
Exit code 1 if errors, 0 otherwise (warnings do not fail).
"""
import csv
import sys
from pathlib import Path

ORDER = ["contradicted", "unresolved", "hypothesis", "single-source", "corroborated", "strongly-corroborated"]
RANK = {s: i for i, s in enumerate(ORDER)}
ORIGINAL_KINDS = {"original", "contemporary-copy"}


def read(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def split(v):
    return [x.strip() for x in (v or "").replace(";", ",").split(",") if x.strip()]


def main(argv) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    case = Path(argv[0])
    reg = case / "registers"
    arts = {a["artifact_id"]: a for a in read(reg / "artifacts.csv") if a.get("artifact_id")}
    claims = {c["claim_id"]: c for c in read(reg / "claims.csv") if c.get("claim_id")}
    persons = {p["person_id"] for p in read(reg / "persons.csv") if p.get("person_id")}
    rels = read(reg / "relationships.csv")
    errors, warnings = [], []

    for aid, a in arts.items():
        if not (a.get("repository") and (a.get("shelfmark") or a.get("url"))):
            warnings.append(f"artifact {aid}: no repository + shelfmark/url")
        if not a.get("independence_group"):
            warnings.append(f"artifact {aid}: no independence_group")
        if (a.get("read_quality") or "").lower() in {"provisional", "doubtful", "downsized"}:
            warnings.append(f"artifact {aid}: reading is {a['read_quality']} — needs manual check")
        f = a.get("file")
        if f and not (case / f).exists() and not Path(f).exists():
            warnings.append(f"artifact {aid}: file not found: {f}")

    for cid, c in claims.items():
        status = (c.get("status") or "").strip()
        if status not in RANK:
            errors.append(f"claim {cid}: unknown status '{status}'")
            continue
        ids = split(c.get("artifact_ids"))
        missing = [i for i in ids if i not in arts]
        if missing:
            errors.append(f"claim {cid}: unknown artifact(s) {missing}")
        groups = {arts[i].get("independence_group") or i for i in ids if i in arts}
        groups |= set(split(c.get("independence_groups"))) if not ids else set()
        n = len(groups)
        if status in {"single-source", "corroborated", "strongly-corroborated"} and n == 0:
            errors.append(f"claim {cid}: '{status}' without artifacts")
        if status in {"corroborated", "strongly-corroborated"} and n < 2:
            errors.append(f"claim {cid}: '{status}' but only {n} independence group(s) — copies do not corroborate")
        if status == "strongly-corroborated":
            if not any((arts[i].get("kind") or "") in ORIGINAL_KINDS for i in ids if i in arts):
                errors.append(f"claim {cid}: 'strongly-corroborated' without an original record")
        if (c.get("kind") or "") in {"family-tradition", "researcher-conclusion"} and RANK[status] > RANK["single-source"]:
            warnings.append(f"claim {cid}: kind '{c['kind']}' graded '{status}' — check independent records")

    for r in rels:
        rid = r.get("rel_id", "?")
        for side in ("person_a", "person_b"):
            if persons and r.get(side) and r[side] not in persons:
                errors.append(f"relationship {rid}: unknown {side} {r[side]}")
        cids = split(r.get("claim_ids"))
        if not cids:
            warnings.append(f"relationship {rid}: no supporting claims")
            continue
        unknown = [c for c in cids if c not in claims]
        if unknown:
            errors.append(f"relationship {rid}: unknown claim(s) {unknown}")
        known = [claims[c].get("status") for c in cids if c in claims and claims[c].get("status") in RANK]
        st = r.get("status")
        if known and st in RANK and RANK[st] > max(RANK[k] for k in known):
            errors.append(f"relationship {rid}: status '{st}' stronger than its best claim")

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("WARN   ", w)
    print(f"\n{len(arts)} artifacts, {len(claims)} claims, {len(rels)} relationships — "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

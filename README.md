# genealogy-research

### Evidence-first genealogy skill and sub-agent harness for Belarus, Lithuania and Poland

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![validate](https://github.com/chocianowicz/genealogy-research/actions/workflows/validate.yml/badge.svg)](https://github.com/chocianowicz/genealogy-research/actions/workflows/validate.yml)
![Python 3 standard library only](https://img.shields.io/badge/python-3%20stdlib%20only-informational)

For AI agents (Claude Code, claude.ai Skills, Codex and other runtimes), covering the Grand Duchy of Lithuania,
the Polish-Lithuanian Commonwealth, the Russian Empire and the USSR.

It teaches an agent to find original records online (revision lists, estate inventories, metric books, court
books, szlachta files, deportation records), download and verify scans, read old handwriting, and grade every
conclusion by its evidence, without inventing shelfmarks, merging namesakes or bypassing site protections.

> **Your private data stays safe.** The repository is plain text files and local Python scripts that use only
> the standard library: nothing is uploaded, tracked or sent anywhere, and no family data ships with it. Your
> research lives in your own case folder on your machine, and archive requests are drafted for you, never sent.
> Your AI tool still sees whatever you give it, so share only what you are comfortable with
> (`templates/share_safely.md`).

**Topics:** genealogy · family history · archival research · Belarus · Lithuania · Poland · Grand Duchy of
Lithuania · Russian Empire · revision lists · metric books · paleography · Claude Code skill · AI agents

## What's inside

```
SKILL.md                     the skill: hard rules, evidence statuses, workflow, harness, done criteria
references/
  evidence-protocol.md       artifact assessment, independence groups, identity resolution, regional traps
  historical-context.md      GDL units, wołoka reform, inventories, partitions, szlachta verification,
                             revisions 1795–1858, 1839 Uniate abolition, 1861, XX c.
  name-variants.md           pl/be/ru/lt/la spelling rules, diminutives, transliterations, female forms
  sources.md                 archives and portals with reliability classes (BY, LT, PL, RU/USSR, published)
  site-techniques.md         tested access patterns: epaveldas.lt, elibrary.mab.lt (DSpace REST),
                             FamilySearch films, Geneteka, Wayback Machine; saving and verifying scans
  paleography.md             Polish secretary hand, Ruthenian Cyrillic, pre-1918 Russian, Latin; dates
agents/
  archive-scout.md           locates holdings (fond/opis/delo, DGS films, online items) for a place/estate/years
  film-mapper.md             maps hundreds of unindexed images by estate/parish/year and scans target ranges
  scan-reader.md             diplomatic transcription + translation + name list with uncertainty marks
  evidence-auditor.md        independent audit of claims and reports before anything is called "established"
scripts/                     Python 3 standard library only
  init_case.py               create a case folder with registers and templates
  hash_artifacts.py          SHA-256 of scans; write/check SHA256SUMS
  verify_epaveldas_md5.py    verify epaveldas downloads by the MD5 in their file names; match renamed temp files
  audit_claims.py            integrity + evidence-strength audit of the claims/relationships registers
  privacy_audit.py           scan files and git history for private terms (local denylist) and personal-data patterns
  validate_repo.py           check skill/agent frontmatter, links, scripts and evals
templates/                   intake, place card, person card, scan README, report, archive request, links-later,
                             share-safely checklist
.github/workflows/           CI: structure validation and privacy scan on every push
evals/scenarios.yaml         behaviour checks (triggers, evidence logic, safety)
install.sh                   one-command install for Claude Code
```

## Core principles

- **Artifacts, not facts** — every find is assessed for origin, directness, legibility and independence.
- **Independence groups** — copies, indexes and retellings of one record never corroborate each other.
- **Statuses, not percentages** — `hypothesis` · `single-source` · `corroborated` · `strongly-corroborated` ·
  `contradicted` · `unresolved`.
- **No namesake merging** without a distinguishing link; **same surname ≠ kinship**.
- **Jurisdiction on the event date** — voivodeship/powiat → gubernia/uezd/volost → interwar → Soviet; estate
  owner and parish of each confession, because records are filed that way.
- **Absence is not evidence** — negative results are logged with their exact scope.
- **Safe by design** — no CAPTCHA/paywall/login bypass, no passwords, minimal data on living people,
  archive requests drafted but never sent by the agent.

## Agent harness

The main agent keeps the reasoning; sub-agents do long or independent work and write results to files:

| Agent | Job | Output |
|---|---|---|
| `archive-scout` | which archive/fond/film holds the records | holdings table, gaps, blocked sources, search log |
| `film-mapper` | map and scan large unindexed image sets | image-range map, hits, fully-read ranges, unread ranges |
| `scan-reader` | read old documents | transcription, translation, names with positions, watch-list hits |
| `evidence-auditor` | independent check before reporting | corrected statuses, namesake risks, decisive next records |

Briefs are complete (agents start cold), results are append-only addenda (they survive rate limits and
restarts), independent agents run in parallel, and the auditor never audits its own work.

## Install

**Claude Code** (user scope, or pass a project path):
```sh
git clone https://github.com/chocianowicz/genealogy-research.git
cd genealogy-research && ./install.sh            # or ./install.sh /path/to/project
```
Skill → `~/.claude/skills/genealogy-research/`, agents → `~/.claude/agents/`.

**claude.ai / Claude apps:** zip the repository folder (with `SKILL.md` at its root) and upload it as a skill.
Sub-agent files can be used as prompts for delegated tasks.

**Codex / other runtimes:** point the agent at `SKILL.md` (e.g. reference it from `AGENTS.md`); use the files in
`agents/` as sub-agent system prompts.

## Quick start

```text
You: Use genealogy-research. My great-grandfather Ivan (b. ~1864) lived in village X, Y uezd, Minsk gubernia.
     Find him in revision lists and metric books.
Agent: intake → place card (owners & parishes by year) → name-variant matrix → archive-scout →
       film-mapper on the revision films → scan-reader on hits → claims graded → evidence-auditor → report.
```

```sh
python3 scripts/init_case.py ~/research/my-case
python3 scripts/hash_artifacts.py --write ~/research/my-case/media/1795_revision_X
python3 scripts/audit_claims.py ~/research/my-case
```

## Contributing

Add sources with: owner · jurisdiction · collection type · originals or index · stable ID format · access ·
restrictions · common errors · date checked. Never add personal data of real families to this repository.

Before every push:
```sh
python3 scripts/validate_repo.py
mkdir -p .private && printf '%s\n' 'Surname' 'Village' > .private/anonymization-denylist.txt   # once; git-ignored
python3 scripts/privacy_audit.py --history
```
The denylist holds the real surnames, villages and names from your own research. It never leaves your machine;
CI can only run the generic patterns (e-mails, phone numbers, 11-digit IDs).

## License

MIT. See `LICENSE`.

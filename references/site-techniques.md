# Site techniques (tested patterns)

General order when a site does not open: cloud shell → user's built-in/real browser → Wayback Machine →
stop and ask the user (CAPTCHA, login, Cloudflare). Never bypass protection.

## epaveldas.lt
- Item page: `https://www.epaveldas.lt/preview?id=<ID>` (IDs like `MAB04-0000NNNNN`, `LVIA…`).
- Metadata (XML-ish, view as text): `https://www.epaveldas.lt/vepis-api/internal/findById?id=<ID>`.
- Page originals: `/static/lmavb-bucket/<ID>/original/NNNN-<MD5UPPER>.jpg`. The hash in the file name is the
  MD5 of the file — use it to verify downloads. The URLs appear in the browser's network log while paging.
- The "Atsisiųsti" (Download) button saves the *current* page only; page through and download each.
- Browser downloads may land as hidden temp files; check type with `file`, verify MD5, then rename.
- Shell/cURL access is often blocked; use the browser.

## elibrary.mab.lt (LMAVB DSpace 7)
- Search UI: `/search?query=<text>`; pages: `&spc.page=2`.
- REST (open in browser, read page text):
  `/server/api/discover/search/objects?query=<text>` — returns title, date, description, shelfmark
  (`dc.identifier.other`, e.g. `F43-NNNN`), subject (place with former powiat), PDF bitstream name
  (number = epaveldas ID suffix).
- Use it to enumerate a whole estate or fond (search by the Lithuanian form of the estate name), then fetch
  scans from epaveldas.

## FamilySearch
- User must be logged in; work in the user's browser. Throttle: slow paging, pauses, no parallel hammering.
- Film viewer: `https://www.familysearch.org/ark:/61903/3:1:<ID>?i=<n>&cat=<catalog>`; DGS numbers in catalogue.
- Unindexed revision films: first map cover/title sheets (estate, owner, year), then read target ranges fully.

## Geneteka
- Use the site's own search form; few queries; record parameters; never bulk-export.

## Wayback Machine
- `https://web.archive.org/web/2024*/example.org/*` lists captures; attachments are archived only if someone
  opened them; try both the page and attachment URL; try several capture years.

## FamilySearch / archive catalogue pages via fetch tools
- Many catalogue pages render client-side; if a fetch tool returns an empty shell, use the browser.

## Saving
- Folder per document: `<YYYY[-MM-DD]>_<doctype>_<place>_<ID>/p0001.jpg …` + README (`templates/scan_readme.md`).
- Hash: `python3 scripts/hash_artifacts.py <folder>` → `SHA256SUMS` and `artifacts` rows.
- Verify epaveldas files: `python3 scripts/verify_epaveldas_md5.py <file_or_dir>`.
- Keep originals; never overwrite. Merge to PDF only as an extra copy.

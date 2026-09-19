# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-09-20

Initial public release.

### Added
- `csv-peek <file>` — one-command profile of a CSV/TSV: column count, data-row count,
  detected delimiter, and a per-column table (inferred type, null %, unique count,
  min/median/max for numbers, top values for text).
- Approximate duplicate-row detection (exact raw-row match) with one example printed.
- `--rows N` head-scan cap (default 50000) for large files; output says `sampled` when capped.
- `--top N` to control how many top values are shown per text column (default 3).
- stdin mode (`csv-peek -`) so it drops into shell pipelines.
- Auto-detection of `,` `;` tab and `|` delimiters, BOM/UTF-8 tolerance, quoted fields
  containing the delimiter, and ragged rows.
- Non-zero exit with a plain message on an empty file (fails loudly in CI rather than silently).
- 7 unit tests (`python3 -m unittest discover -s tests -v`).

### Notes
- Zero dependencies: Python 3.8+ standard library only, single file, no install step.
- Read-only and local: it never uploads the file and never calls a model.
- Known limits are listed in the README ("Limitations (honest list)") — heuristic type
  inference, head-only sampling on very large files, no Excel support.

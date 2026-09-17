# csv-peek

**Profile any CSV/TSV from your terminal — before you load it into pandas or SQL.**

Zero dependencies. Python 3.8+ standard library only. One file, ~140 lines.

```
$ csv-peek data.csv

file      : data.csv
size      : 412.7 KB
delimiter : ','
columns   : 5
data rows : 12043

  #  name    age     city    total_spend  signup_date
  -------------------------------------------------------
   0  name               text   null  0.0%  uniq 4201   Alice×2 | Bob×1 | Cara×1
   1  age                int    null 20.0%  uniq 3      min 29 · med 34 · max 41
   2  city               text   null  0.0%  uniq 4      Shanghai×2 | Beijing×1 | Shenzhen×1
   3  total_spend        float  null 20.0%  uniq 3      min 12 · med 1062.25 · max 1234.5
   4  signup_date        date   null  0.0%  uniq 4      2024-01-05×2 | 2024-02-11×1 | 2024-03-02×1

⚠️  possible duplicate rows: 1
    ×2  ('Alice', '34', 'Shanghai', '1,234.50', '2024-01-05')
```

## Why

Every data task starts the same way: *what is actually in this file?* Normally you open a
notebook, import pandas, and run five cells. `csv-peek` answers it in one command, with no
environment to set up — useful in a terminal, a server, a CI job, or a cron script.

It tells you, per column:

- **inferred type** (int / float / date / text) — so you know what will break on import
- **null percentage** — the number that ruins aggregations
- **unique count** — is this a key, a category, or free text?
- **min / median / max** for numbers, **top values** for text
- **duplicate rows** — counted, with an example

## Install

```bash
# no install needed — run it directly
curl -O https://raw.githubusercontent.com/CindyLiao1106/csv-peek/main/csv_peek.py
python3 csv_peek.py data.csv

# or make it a command
chmod +x csv_peek.py && mv csv_peek.py ~/.local/bin/csv-peek
```

## Usage

```bash
csv-peek data.csv                 # full profile
csv-peek data.tsv --top 5         # more top values per text column
csv-peek big.csv --rows 2000      # sample only the first 2000 rows (fast)
cat data.csv | csv-peek -         # stdin works too
csv-peek export.csv > profile.txt # save the profile next to your data
```

Options:

| flag | default | meaning |
|---|---|---|
| `--rows N` | 50000 | max data rows to scan |
| `--top N` | 3 | top values shown per text column |

Handles `,` `;` `\t` `|` delimiters automatically, plus BOM/UTF-8 issues
(`errors="ignore"`), quoted fields with commas, and files with ragged rows.

## When you need more than a profile

`csv-peek` is deliberately read-only and local: it never uploads your file, never calls a
model, and prints nothing you didn't ask for.

When you want to **ask questions about the data in plain English** ("which city has the highest
average spend per signup month?"), that's the hosted AI version:
**https://nocodecsv.com** — files are parsed in your browser, and only the columns you select
are sent for analysis. Free tier covers 3 analyses per day.

## Limitations (honest list)

- Type inference is heuristic: `20240301` and `12-13-2024` still classify as int/text.
  It reports what it sees rather than guessing a format.
- Dates are detected but not parsed into a real date type — this tool doesn't compute date ranges.
- `--rows` scans the head of the file only, so null/unique numbers are estimates on large files
  (it says "sampled" when it hits the cap).
- No Excel support (that needs a real xlsx reader — out of scope for a zero-dependency tool).
- Duplicate detection is exact-match on the raw row; `"1,234.50"` and `1234.5` don't match.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT

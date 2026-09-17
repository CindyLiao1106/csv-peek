#!/usr/bin/env python3
"""
csv-peek — quick profile of any CSV/TSV from the terminal.

Zero dependencies (Python 3.8+ standard library only).

Usage:
    csv-peek data.csv
    csv-peek data.tsv --rows 5 --top 5
    cat data.csv | csv-peek -

What it prints:
    · detected delimiter, row/column counts, file size
    · per-column: inferred type, null %, unique count, min/max or top values
    · possible duplicate rows and the first few

Why: before you load a CSV into pandas/SQL, you want to know what is actually in it.
"""
import argparse
import csv
import io
import os
import statistics
import sys
from collections import Counter

NULLS = {"", "na", "n/a", "null", "none", "-", "nan", "nil"}


def sniff(path_or_dash, sample_size=65536):
    if path_or_dash == "-":
        raw = sys.stdin.read()
        try:
            dialect = csv.Sniffer().sniff(raw[:sample_size], delimiters=",;\t|")
            delim = dialect.delimiter
        except Exception:
            delim = ","
        return io.StringIO(raw), len(raw), delim
    with open(path_or_dash, "rb") as fh:
        sample = fh.read(sample_size)
    size = os.path.getsize(path_or_dash)
    try:
        dialect = csv.Sniffer().sniff(sample.decode("utf-8", "ignore"), delimiters=",;\t|")
        delim = dialect.delimiter
    except Exception:
        delim = "\t" if path_or_dash.lower().endswith((".tsv", ".tab")) else ","
    return open(path_or_dash, "r", encoding="utf-8", errors="ignore", newline=""), size, delim


def infer_type(values):
    if not values:
        return "empty"
    nums, ints, dates = 0, 0, 0
    for v in values:
        s = v.strip()
        try:
            f = float(s.replace(",", ""))
            nums += 1
            if f == int(f):
                ints += 1
        except ValueError:
            if len(s) >= 8 and (s[:4].isdigit() or s[:2].isdigit()) and ("-" in s or "/" in s):
                dates += 1
    n = len(values)
    if dates / n > 0.8:
        return "date"
    if nums / n > 0.95:
        return "int" if ints / n > 0.95 else "float"
    return "text"


def profile(path, max_rows=None, top=3, sample_cols=None):
    fh, size, delim = sniff(path)
    reader = csv.reader(fh, delimiter=delim)
    try:
        header = next(reader)
    except StopIteration:
        print("empty file")
        return 1
    cols = len(header)
    data = []
    for i, row in enumerate(reader):
        if max_rows and i >= max_rows:
            break
        data.append(row)

    print(f"file      : {path}")
    print(f"size      : {size/1024:.1f} KB")
    print(f"delimiter : {repr(delim)}")
    print(f"columns   : {cols}")
    print(f"data rows : {len(data)}{' (sampled)' if max_rows and len(data) >= max_rows else ''}")
    print()

    widths = [max(len(str(header[c])), 6) for c in range(cols)]
    print("  #  " + "  ".join(f"{str(header[c])[:widths[c]]:<{widths[c]}}" for c in range(cols)))
    print("  " + "-" * (sum(widths) + 2 * cols + 5))

    for c in range(cols):
        values = [r[c] for r in data if c < len(r)]
        total = len(values) or 1
        nulls = sum(1 for v in values if v.strip().lower() in NULLS)
        nonnull = [v for v in values if v.strip().lower() not in NULLS]
        t = infer_type(nonnull)
        uniq = len(set(nonnull))
        detail = ""
        if t in ("int", "float") and nonnull:
            nums = []
            for v in nonnull:
                try:
                    nums.append(float(v.replace(",", "")))
                except ValueError:
                    pass
            if nums:
                detail = f"min {min(nums):g} · med {statistics.median(nums):g} · max {max(nums):g}"
        else:
            common = Counter(nonnull).most_common(top)
            detail = " | ".join(f"{v[:16]}×{n}" for v, n in common)
        print(f"  {c:>2} {header[c][:22]:<22} {t:<6} null {nulls/total*100:>4.1f}%  uniq {uniq:<6} {detail[:60]}")

    # duplicates
    if data:
        seen = Counter(tuple(r) for r in data)
        dups = sum(n - 1 for n in seen.values() if n > 1)
        if dups:
            print(f"\n⚠️  possible duplicate rows: {dups}")
            for row, n in list(seen.items())[:2]:
                if n > 1:
                    print(f"    ×{n}  {str(row)[:110]}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Quick CSV/TSV profile — zero dependencies.")
    ap.add_argument("path", help="CSV/TSV file, or - for stdin")
    ap.add_argument("--rows", type=int, default=50000, help="max data rows to scan (default 50000)")
    ap.add_argument("--top", type=int, default=3, help="top values per text column (default 3)")
    a = ap.parse_args()
    try:
        sys.exit(profile(a.path, a.rows, a.top))
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()

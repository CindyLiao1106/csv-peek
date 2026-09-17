"""Tests for csv-peek. Run: python3 -m unittest discover -s tests -v"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(HERE, "csv_peek.py")
PY = sys.executable

SAMPLE = """name,age,city,total_spend,signup_date
Alice,34,Shanghai,"1,234.50",2024-01-05
Bob,,Beijing,890.00,2024-02-11
Alice,34,Shanghai,"1,234.50",2024-01-05
Cara,41,Shenzhen,,2024-03-02
"""


def run(args, stdin=None, cwd=HERE):
    return subprocess.run([PY, SCRIPT] + args, input=stdin, capture_output=True, text=True, cwd=cwd)


class TestCsvPeek(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "sample.csv")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(SAMPLE)

    def test_reports_shape(self):
        r = run([self.path])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("columns   : 5", r.stdout)
        self.assertIn("data rows : 4", r.stdout)

    def test_infers_types_and_nulls(self):
        r = run([self.path])
        self.assertIn("int", r.stdout)      # age
        self.assertIn("float", r.stdout)    # total_spend
        self.assertIn("date", r.stdout)     # signup_date
        self.assertIn("null 25.0%", r.stdout)  # age has 1 empty of 4

    def test_detects_duplicates(self):
        r = run([self.path])
        self.assertIn("possible duplicate rows: 1", r.stdout)

    def test_semicolon_delimiter(self):
        p = os.path.join(self.tmp, "semi.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("a;b\n1;x\n2;y\n")
        r = run([p])
        self.assertIn("delimiter : ';'", r.stdout)
        self.assertIn("columns   : 2", r.stdout)

    def test_stdin_mode(self):
        r = run(["-"], stdin=SAMPLE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("columns   : 5", r.stdout)

    def test_rows_cap(self):
        r = run([self.path, "--rows", "2"])
        self.assertIn("data rows : 2", r.stdout)
        self.assertIn("sampled", r.stdout)

    def test_empty_file_exits_nonzero_with_message(self):
        """An empty file is an error condition (exit 1), and it says so plainly."""
        p = os.path.join(self.tmp, "empty.csv")
        open(p, "w").close()
        r = run([p])
        self.assertEqual(r.returncode, 1)
        self.assertIn("empty file", r.stdout)


if __name__ == "__main__":
    unittest.main()

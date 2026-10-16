# csv-peek

**ターミナルからそのまま CSV/TSV をプロファイリング —— pandas や SQL に読み込む前に。**

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md)

依存ゼロ。Python 3.8+ の標準ライブラリのみ。1 ファイル、約 140 行。

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

## なぜ作ったか

データ作業の出だしはいつも同じです：**このファイルの中身は実際どうなっているのか？**
普通はノートブックを開き、`import pandas` して、セルを 5 つ実行します。`csv-peek` はそれを
コマンド 1 つで答えます。環境構築は不要で、ターミナル・サーバー・CI ジョブ・cron スクリプトで動きます。

列ごとに分かること：

- **推定型**（int / float / date / text）—— 読み込み時にどこで壊れるかが分かる
- **null 率** —— 集計を台無しにするあの数字
- **ユニーク数** —— この列はキーなのか、カテゴリなのか、自由記述なのか
- **min / median / max**（数値列）、**出現回数の多い値**（テキスト列）
- **重複行** —— 件数と 1 例

## インストール

```bash
# インストール不要 —— そのまま実行
curl -O https://raw.githubusercontent.com/CindyLiao1106/csv-peek/main/csv_peek.py
python3 csv_peek.py data.csv

# コマンドとして使う場合
chmod +x csv_peek.py && mv csv_peek.py ~/.local/bin/csv-peek
```

## 使い方

```bash
csv-peek data.csv                 # フルプロファイル
csv-peek data.tsv --top 5         # テキスト列ごとの上位値を増やす
csv-peek big.csv --rows 2000      # 先頭 2000 行だけサンプリング(高速)
cat data.csv | csv-peek -         # 標準入力にも対応
csv-peek export.csv > profile.txt # プロファイルをデータの隣に保存
```

オプション：

| フラグ | 既定値 | 意味 |
|---|---|---|
| `--rows N` | 50000 | スキャンするデータ行の上限 |
| `--top N` | 3 | テキスト列ごとに表示する上位値の数 |

区切り文字 `,` `;` `\t` `|` を自動判別し、BOM/UTF-8 の問題
（`errors="ignore"`）、カンマを含む引用フィールド、列数が揃わない行にも耐えます。

## プロファイルだけでは足りないとき

`csv-peek` は意図的に読み取り専用かつローカルです：ファイルをアップロードせず、モデルを呼ばず、
頼んでいないものは何も出力しません。

**自然言語でデータに質問したい**場合（例：「登録月ごとの平均消費が最も高い都市は？」）は、
ホスト版の AI があります：**https://nocodecsv.com** —— ファイルはブラウザ内で解析され、
選択した列だけが分析に送られます。無料枠は 1 日 3 回まで。

## 制限事項（正直なリスト）

- 型推論はヒューリスティックです：`20240301` や `12-13-2024` は int/text に分類されたままです。
  フォーマットを推測せず、見えたままを報告します。
- 日付は検出だけを行い、実際の日付型には変換しません —— このツールは期間計算をしません。
- `--rows` はファイル先頭だけをスキャンするため、大きなファイルでの null/ユニーク数は推定値です
  （上限に達すると出力に `sampled` と表示されます）。
- Excel 非対応（本物の xlsx リーダーが必要で、依存ゼロのツールの範囲外です）。
- 重複検出は行全体の完全一致です；`\"1,234.50\"` と `1234.5` は一致しません。

## テスト

```bash
python3 -m unittest discover -s tests -v
```

## ライセンス

MIT

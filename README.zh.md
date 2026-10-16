# csv-peek

**在终端里直接剖析任意 CSV/TSV —— 在你把它读进 pandas 或 SQL 之前。**

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md)

零依赖。只用 Python 3.8+ 标准库。单文件，约 140 行。

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

## 为什么

每个数据任务的开场都一样：**这个文件里到底是什么？** 通常你要打开 notebook、`import pandas`、再跑五个 cell。
`csv-peek` 用一条命令回答这个问题，而且不需要配环境 —— 终端、服务器、CI 任务、cron 脚本里都能用。

它按列告诉你：

- **推断类型**（int / float / date / text）—— 让你知道导入时哪里会炸
- **空值百分比** —— 毁掉聚合结果的那个数
- **唯一值数量** —— 这列是主键、分类，还是自由文本？
- **min / median / max**（数值列），**出现最多的取值**（文本列）
- **重复行** —— 计数，并给出一个例子

## 安装

```bash
# 无需安装 —— 直接运行
curl -O https://raw.githubusercontent.com/CindyLiao1106/csv-peek/main/csv_peek.py
python3 csv_peek.py data.csv

# 或者把它变成一条命令
chmod +x csv_peek.py && mv csv_peek.py ~/.local/bin/csv-peek
```

## 用法

```bash
csv-peek data.csv                 # 完整剖析
csv-peek data.tsv --top 5         # 每个文本列多显示几个高频值
csv-peek big.csv --rows 2000      # 只抽样前 2000 行（更快）
cat data.csv | csv-peek -         # 也支持标准输入
csv-peek export.csv > profile.txt # 把剖析结果存到数据旁边
```

选项：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `--rows N` | 50000 | 最多扫描的数据行数 |
| `--top N` | 3 | 每个文本列显示的高频值个数 |

自动识别 `,` `;` `\t` `|` 分隔符，并容忍 BOM/UTF-8 问题
（`errors="ignore"`）、字段内带逗号的引号值，以及列数不齐的行。

## 当一次剖析不够用时

`csv-peek` 刻意只读、只在本机运行：它从不上传你的文件，从不调用模型，也不会打印你没要的东西。

当你想**用自然语言对数据提问**（比如"哪个城市的每月注册平均消费最高？"），那是托管版 AI：
**https://nocodecsv.com** —— 文件在你的浏览器里解析，只把你勾选的列送去分析。免费额度每天 3 次。

## 局限（诚实清单）

- 类型推断是启发式的：`20240301` 和 `12-13-2024` 仍会被归为 int/text。
  它只报告它看到的东西，不猜格式。
- 日期只做识别，不解析成真正的日期类型 —— 这个工具不算日期区间。
- `--rows` 只扫文件头部，所以大文件上的空值/唯一值数字是估计值
  （触顶时输出会标 `sampled`）。
- 不支持 Excel（那需要真正的 xlsx 解析器 —— 超出一个零依赖工具的范围）。
- 重复检测是按整行原文精确匹配；`"1,234.50"` 和 `1234.5` 不匹配。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 许可证

MIT

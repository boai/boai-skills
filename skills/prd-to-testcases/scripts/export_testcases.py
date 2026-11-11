#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Markdown / CSV 测试用例表导出为带格式的 Excel，并生成覆盖统计。"""

import argparse
import csv
import os
import re
import sys
from collections import Counter, OrderedDict

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

DEFAULT_COLUMNS = ["编号", "模块", "功能点", "用例标题", "类型", "优先级",
                   "前置条件", "操作步骤", "预期结果", "需求来源", "执行结果"]
REQUIRED_HEADERS = ("编号", "用例标题", "预期结果")
WIDTHS = {
    "编号": 18, "模块": 14, "功能点": 20, "用例标题": 28, "类型": 8,
    "优先级": 8, "前置条件": 28, "操作步骤": 42, "预期结果": 42,
    "需求来源": 12, "执行结果": 10,
}
TYPES = ["功能", "异常", "边界", "权限", "兼容"]
ALL_TYPES = TYPES + ["性能", "安全"]
PRIORITY_FILL = {}
if HAS_OPENPYXL:
    PRIORITY_FILL = {
        "P0": PatternFill("solid", fgColor="FCE4E4"),
        "P1": PatternFill("solid", fgColor="FFF2CC"),
        "P2": PatternFill("solid", fgColor="EDEDED"),
    }


def die(message):
    print("错误：%s" % message, file=sys.stderr)
    sys.exit(2)


def clean_cell(cell):
    return re.sub(r"<br\s*/?>", "\n", cell.strip(), flags=re.IGNORECASE)


def parse_table_block(block):
    rows = []
    for line in block:
        cells = [clean_cell(c) for c in line.strip("|").split("|")]
        if not cells:
            continue
        if all(c and set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells)
    return rows


def parse_markdown(path):
    """只挑出表头含 编号/用例标题/预期结果 的测试用例表，忽略功能点表、待确认问题表等。"""
    tables = []
    current = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("|"):
                current.append(stripped)
            elif current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    if not tables:
        die("没有在文件中找到 Markdown 表格，请确认表头以 | 开头")

    merged_header = None
    merged_rows = []
    for block in tables:
        rows = parse_table_block(block)
        if not rows:
            continue
        header = rows[0]
        if all(key in header for key in REQUIRED_HEADERS):
            if merged_header is None:
                merged_header = header
            merged_rows.extend(rows[1:])
    if merged_header is None:
        die("未找到测试用例表：表头需要包含 %s" % " / ".join(REQUIRED_HEADERS))
    return merged_header, merged_rows


def parse_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        rows = [[clean_cell(c) for c in row] for row in reader if any(c.strip() for c in row)]
    if not rows:
        die("CSV 文件为空")
    return rows[0], rows[1:]


def normalize(header, data):
    header = [h.strip() for h in header]
    missing = [c for c in REQUIRED_HEADERS if c not in header]
    if missing:
        die("缺少关键列：%s" % "、".join(missing))

    index = {name: i for i, name in enumerate(header)}
    records = []
    for row in data:
        if not any(cell.strip() for cell in row):
            continue
        record = OrderedDict()
        for col in DEFAULT_COLUMNS:
            i = index.get(col)
            record[col] = row[i].strip() if i is not None and i < len(row) else ""
        records.append(record)
    if not records:
        die("表格只有表头，没有用例数据")
    return records


def write_xlsx(records, out_path, force=False):
    if not HAS_OPENPYXL:
        die("生成 Excel 需要 openpyxl，请先运行: python3 -m pip install --user openpyxl")
    if os.path.exists(out_path) and not force:
        die("输出文件已存在：%s（加 --force 覆盖）" % out_path)

    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"

    # 固定列，即使「执行结果」全为空也保留，方便测试填写
    columns = DEFAULT_COLUMNS
    ws.append(columns)

    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col_idx, name in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
        ws.column_dimensions[get_column_letter(col_idx)].width = WIDTHS.get(name, 18)

    for record in records:
        ws.append([record.get(c, "") for c in columns])
        excel_row = ws.max_row
        for col_idx, name in enumerate(columns, 1):
            cell = ws.cell(row=excel_row, column=col_idx)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=(name in ("前置条件", "操作步骤", "预期结果")))
        p = record.get("优先级", "")
        ws.cell(row=excel_row, column=columns.index("优先级") + 1).fill = PRIORITY_FILL.get(p, PRIORITY_FILL["P2"])

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(columns)), len(records) + 1)

    dv = DataValidation(type="list", formula1='"通过,失败,阻塞,未测"', allow_blank=True)
    dv.error = "请选择：通过 / 失败 / 阻塞 / 未测"
    dv.errorTitle = "执行结果"
    ws.add_data_validation(dv)
    idx = columns.index("执行结果") + 1
    dv.add("%s2:%s%d" % (get_column_letter(idx), get_column_letter(idx), len(records) + 1))

    # ---- 覆盖统计 ----
    stats = wb.create_sheet("覆盖统计")
    stats.append(["模块"] + ALL_TYPES + ["合计"])
    for cell in stats[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    by_module = OrderedDict()
    for record in records:
        module = record.get("模块") or "未填写"
        by_module.setdefault(module, Counter())[record.get("类型") or "未填写"] += 1

    type_totals = Counter()
    for module, counter in by_module.items():
        row = [module] + [counter.get(t, 0) for t in ALL_TYPES] + [sum(counter.values())]
        stats.append(row)
        type_totals.update(counter)

    stats.append(["合计"] + [type_totals.get(t, 0) for t in ALL_TYPES] + [sum(type_totals.values())])
    for cell in stats[stats.max_row]:
        cell.font = Font(bold=True)

    stats.column_dimensions["A"].width = 20
    for i in range(2, len(ALL_TYPES) + 3):
        stats.column_dimensions[get_column_letter(i)].width = 8

    start = stats.max_row + 2
    stats.cell(row=start, column=1, value="需求来源覆盖").font = Font(bold=True, size=12)
    stats.cell(row=start + 1, column=1, value="需求来源")
    stats.cell(row=start + 1, column=2, value="用例数")
    for cell in (stats.cell(row=start + 1, column=1), stats.cell(row=start + 1, column=2)):
        cell.fill = header_fill
        cell.font = header_font
    for source, count in Counter(r.get("需求来源") or "未标注" for r in records).most_common():
        stats.append([source, count])
    stats.column_dimensions["B"].width = 10

    wb.save(out_path)

    total = len(records)
    p0 = sum(1 for r in records if r.get("优先级") == "P0")
    modules = len({r.get("模块") for r in records})
    sources = len({r.get("需求来源") for r in records if r.get("需求来源")})
    print("已生成: %s" % os.path.abspath(out_path))
    print("用例总数 %d 条，P0 %d 条，覆盖 %d 个模块、%d 个需求来源。" % (total, p0, modules, sources))

    for module, counter in by_module.items():
        missing = [t for t in TYPES if counter.get(t, 0) == 0]
        if missing:
            print("提示：模块「%s」缺少 %s 类用例" % (module, "、".join(missing)))
    no_source = sum(1 for r in records if not r.get("需求来源"))
    if no_source:
        print("提示：%d 条用例未标注需求来源。" % no_source)


def main():
    parser = argparse.ArgumentParser(description="测试用例 Markdown/CSV 导出 Excel")
    parser.add_argument("--input", required=True, help="Markdown 或 CSV 用例表")
    parser.add_argument("--out", default="", help="输出 xlsx 路径，默认与输入同名")
    parser.add_argument("--force", action="store_true", help="输出文件已存在时覆盖")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        die("输入文件不存在：%s" % args.input)

    if args.input.lower().endswith(".csv"):
        header, data = parse_csv(args.input)
    else:
        header, data = parse_markdown(args.input)

    records = normalize(header, data)
    out_path = args.out or os.path.splitext(args.input)[0] + ".xlsx"
    write_xlsx(records, out_path, force=args.force)


if __name__ == "__main__":
    main()

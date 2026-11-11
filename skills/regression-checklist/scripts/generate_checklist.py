#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 Git 改动 + 项目模块地图，生成回归测试清单（XLSX / Markdown / CSV）。"""

import argparse
import csv
import fnmatch
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

EXCLUDES = [
    ":(exclude,glob)*.lock",
    ":(exclude,glob)*.pbxproj",
    ":(exclude,glob)xcuserdata/**",
    ":(exclude,glob)Pods/**",
    ":(exclude,glob)node_modules/**",
    ":(exclude,glob)build/**",
    ":(exclude,glob)DerivedData/**",
]

# 路径关键词 -> (回归原因, 优先级)
GLOBAL_RULES = [
    (("Network/", "APIClient", "HttpClient", "NetworkClient", "APIRequest"),
     "网络层变更，所有依赖接口的模块需回归", "P1"),
    (("Localizable", "Resources/", ".strings", ".xcstrings"),
     "文案/资源变更，抽查关键页面、多语言与长文案", "P2"),
    (("Common/", "Utils/", "Extensions/", "Helper"),
     "公共组件变更，所有引用方需回归", "P1"),
    (("AppDelegate", "SceneDelegate", "main.swift", "Launch"),
     "启动流程变更，需全量冒烟", "P0"),
    (("Login", "Auth", "Token", "Session", "Account"),
     "登录态变更，需回归登录/登出/切换账号/过期", "P0"),
]

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def run_git(args, cwd):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git 命令执行失败")
    return result.stdout


def detect_base(repo):
    for candidate in ("origin/HEAD", "main", "master"):
        try:
            out = run_git(["symbolic-ref", "refs/remotes/" + candidate, "--short"], repo).strip()
            if out:
                return out.split("/")[-1]
        except RuntimeError:
            pass
        try:
            run_git(["rev-parse", "--verify", "--quiet", candidate], repo)
            return candidate
        except RuntimeError:
            continue
    raise RuntimeError("无法自动识别基线分支，请用 --base 指定")


def get_changed_files(args):
    if args.files:
        return [f.strip() for f in args.files if f.strip()]
    base = args.base or detect_base(args.repo)
    out = run_git(["diff", "--name-only", "%s...%s" % (base, args.target), "--"] + EXCLUDES, args.repo)
    return [line.strip() for line in out.splitlines() if line.strip()]


def load_map(path):
    if not path or not os.path.isfile(path):
        return None
    if yaml is None:
        raise RuntimeError("读取 YAML 需要 PyYAML，请先运行: python3 -m pip install --user pyyaml")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise RuntimeError("模块地图 YAML 格式错误：%s\n%s" % (path, exc))


def match_path(path, patterns):
    for pattern in patterns or []:
        pattern = str(pattern).strip()
        if not pattern:
            continue
        if any(ch in pattern for ch in "*?["):
            if fnmatch.fnmatch(path, pattern):
                return True
        elif pattern.endswith("/"):
            if path.startswith(pattern):
                return True
        elif path == pattern or path.startswith(pattern + "/"):
            return True
    return False


def build_rows(files, project_map):
    rows = []
    seen = set()
    unmatched = []
    module_hits = {}

    modules = (project_map or {}).get("modules", []) or []
    for path in files:
        matched = False
        for module in modules:
            if match_path(path, module.get("paths")):
                matched = True
                name = module.get("name") or "未命名模块"
                module_hits.setdefault(name, {"files": [], "module": module})
                module_hits[name]["files"].append(path)
        if not matched:
            unmatched.append(path)

    for name, hit in module_hits.items():
        module = hit["module"]
        priority = str(module.get("priority") or "P1").upper()
        steps = module.get("test_steps") or ["按模块主流程执行一遍"]
        reason = "直接改动：%s" % "、".join(sorted(set(hit["files"]))[:3])
        if len(hit["files"]) > 3:
            reason += " 等 %d 个文件" % len(hit["files"])
        for step in steps:
            key = (name, str(step), reason)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "模块": name,
                "功能点": name,
                "回归原因": reason,
                "优先级": priority,
                "验证步骤": str(step),
                "结果": "",
            })

    # 全局规则：公共面改动带来的间接影响
    for path in files:
        for keywords, reason, priority in GLOBAL_RULES:
            if any(k in path for k in keywords):
                key = ("全局", reason, path)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "模块": "全局",
                    "功能点": "受影响公共面",
                    "回归原因": "%s（来源：%s）" % (reason, path),
                    "优先级": priority,
                    "验证步骤": reason,
                    "结果": "",
                })

    rows.sort(key=lambda r: (PRIORITY_ORDER.get(r["优先级"], 9), r["模块"]))
    return rows, unmatched


def write_markdown(rows, unmatched, out_path, project_name):
    lines = ["# %s 回归测试清单" % project_name, "",
             "| # | 模块 | 功能点 | 回归原因 | 优先级 | 验证步骤 | 结果 |",
             "|---|------|--------|----------|--------|----------|------|"]
    for idx, row in enumerate(rows, 1):
        lines.append("| %d | %s | %s | %s | %s | %s |  |" % (
            idx, row["模块"], row["功能点"], row["回归原因"],
            row["优先级"], row["验证步骤"]))
    if unmatched:
        lines += ["", "## 未映射改动（请补充到 .regression-map.yml）", ""]
        for path in unmatched:
            lines.append("- `%s`" % path)
    content = "\n".join(lines) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)
    else:
        sys.stdout.write(content)


def write_csv(rows, out_path):
    handle = open(out_path, "w", encoding="utf-8-sig", newline="") if out_path else sys.stdout
    writer = csv.writer(handle)
    writer.writerow(["序号", "模块", "功能点", "回归原因", "优先级", "验证步骤", "结果"])
    for idx, row in enumerate(rows, 1):
        writer.writerow([idx, row["模块"], row["功能点"], row["回归原因"],
                         row["优先级"], row["验证步骤"], ""])
    if out_path:
        handle.close()


def write_xlsx(rows, unmatched, out_path, project_name):
    if not HAS_OPENPYXL:
        raise RuntimeError("生成 XLSX 需要 openpyxl，请先运行: python3 -m pip install --user openpyxl")

    wb = Workbook()
    ws = wb.active
    ws.title = "回归清单"

    headers = ["序号", "模块", "功能点", "回归原因", "优先级", "验证步骤", "结果"]
    ws.append(headers)

    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    priority_fill = {
        "P0": PatternFill("solid", fgColor="FCE4E4"),
        "P1": PatternFill("solid", fgColor="FFF2CC"),
        "P2": PatternFill("solid", fgColor="EDEDED"),
    }

    for idx, row in enumerate(rows, 1):
        ws.append([idx, row["模块"], row["功能点"], row["回归原因"],
                   row["优先级"], row["验证步骤"], ""])
        excel_row = ws.max_row
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=excel_row, column=col)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=(col in (4, 6)))
        ws.cell(row=excel_row, column=5).fill = priority_fill.get(row["优先级"], priority_fill["P2"])

    widths = [6, 16, 20, 38, 8, 46, 12]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.freeze_panes = "A2"
    if rows:
        ws.auto_filter.ref = "A1:G%d" % (len(rows) + 1)

    dv = DataValidation(type="list", formula1='"通过,失败,阻塞,未测"', allow_blank=True)
    dv.error = "请选择：通过 / 失败 / 阻塞 / 未测"
    dv.errorTitle = "结果取值"
    ws.add_data_validation(dv)
    if rows:
        dv.add("G2:G%d" % (len(rows) + 1))

    if unmatched:
        ws2 = wb.create_sheet("未映射改动")
        ws2.append(["文件路径", "处理建议"])
        for cell in ws2[1]:
            cell.fill = header_fill
            cell.font = header_font
        for path in unmatched:
            ws2.append([path, "补充到 .regression-map.yml 的对应模块"])
        ws2.column_dimensions["A"].width = 70
        ws2.column_dimensions["B"].width = 40

    wb.save(out_path)


def main():
    parser = argparse.ArgumentParser(description="生成回归测试清单")
    parser.add_argument("--repo", default=".", help="仓库路径，默认当前目录")
    parser.add_argument("--base", default="", help="基线分支，默认自动探测")
    parser.add_argument("--target", default="HEAD", help="目标分支/提交")
    parser.add_argument("--files", nargs="*", default=[], help="直接指定改动文件列表（不读 Git）")
    parser.add_argument("--map", default=".regression-map.yml", help="模块地图 YAML 路径")
    parser.add_argument("--format", choices=["xlsx", "md", "csv"], default="xlsx")
    parser.add_argument("--out", default="", help="输出文件路径；不填则 XLSX 默认 回归清单-<日期>.xlsx")
    parser.add_argument("--force", action="store_true", help="输出文件已存在时覆盖")
    args = parser.parse_args()

    if not os.path.isdir(args.repo):
        print("错误：仓库路径不存在：%s" % args.repo, file=sys.stderr)
        return 1

    try:
        files = get_changed_files(args)
    except (RuntimeError, subprocess.SubprocessError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 1

    if not files:
        print("没有检测到改动文件（或全部被过滤），无需生成回归清单。")
        return 0

    project_map = None
    map_path = args.map
    if not os.path.isabs(map_path) and not os.path.isfile(map_path):
        candidate = os.path.join(args.repo, map_path)
        if os.path.isfile(candidate):
            map_path = candidate
    try:
        project_map = load_map(map_path)
    except RuntimeError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    if project_map is None:
        print("提示：未找到模块地图 %s，将仅按全局规则生成清单。" % args.map, file=sys.stderr)

    rows, unmatched = build_rows(files, project_map)
    project_name = (project_map or {}).get("project") or os.path.basename(os.path.abspath(args.repo))

    out_path = args.out
    if args.format == "xlsx" and not out_path:
        out_path = "回归清单-%s.xlsx" % __import__("datetime").date.today().strftime("%Y%m%d")
    if out_path and os.path.exists(out_path) and not args.force:
        print("错误：输出文件已存在：%s（加 --force 覆盖）" % out_path, file=sys.stderr)
        return 2

    try:
        if args.format == "xlsx":
            write_xlsx(rows, unmatched, out_path, project_name)
            print("已生成: %s" % os.path.abspath(out_path))
        elif args.format == "csv":
            write_csv(rows, out_path)
            if out_path:
                print("已生成: %s" % os.path.abspath(out_path))
        else:
            write_markdown(rows, unmatched, out_path, project_name)
            if out_path:
                print("已生成: %s" % os.path.abspath(out_path))
    except RuntimeError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2

    summary_stream = sys.stderr if (not args.out and args.format in ("csv", "md")) else sys.stdout
    p0 = sum(1 for r in rows if r["优先级"] == "P0")
    print("共 %d 条回归项（P0 %d 条），涉及 %d 个模块，未映射文件 %d 个。"
          % (len(rows), p0, len({r["模块"] for r in rows}), len(unmatched)), file=summary_stream)
    if unmatched:
        print("未映射文件：", file=summary_stream)
        for path in unmatched:
            print("  - %s" % path, file=summary_stream)
    return 0


if __name__ == "__main__":
    sys.exit(main())

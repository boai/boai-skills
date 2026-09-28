# 🧰 boai skills

[![version](https://img.shields.io/badge/version-1.6.0-blue.svg)](#版本)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-silver.svg)](#)

> Claude Code 插件 · 实用技能合集，持续更新

## 安装

先把本仓库添加为 marketplace（只需做一次）：

```
/plugin marketplace add boai/boai-skills
```

> 私有仓库会自动走你本机已有的 git 凭证（和 `git clone` 一样），**无需手动 clone 代码**。

### ⭐ claude-token-tracker —— 自动 token 统计（无需触发词）

```
/plugin install claude-token-tracker@boai-skills
```

装完后**重启 Claude Code**（或 `/reload-plugins`）。之后**正常对话即可，每轮回答结束会自动打印 token 统计**（当前对话 / 今日 / 本月 / 历史全部）——它是一个 Stop hook，**不需要你说任何提示词**。

### 其他技能（提到触发词时启用）

整包安装全部技能：

```
/plugin install boai-skills@boai-skills
```

按技能名安装（任装一个都会得到全部技能 —— 这些条目指向同一份清单，版本号也共用同一个）：

| 技能 | 安装命令 |
|------|----------|
| 📝 boai-article-writer | `/plugin install boai-article-writer@boai-skills` |
| 🎬 boai-film-review | `/plugin install boai-film-review@boai-skills` |
| ✈️ boai-travel-guide | `/plugin install boai-travel-guide@boai-skills` |
| 🍜 boai-city-food | `/plugin install boai-city-food@boai-skills` |
| 🧹 sogou-ad-killer | `/plugin install sogou-ad-killer@boai-skills` |
| 🔧 360-cleaner | `/plugin install 360-cleaner@boai-skills` |
| 💬 mac-wechat-dual-instance | `/plugin install mac-wechat-dual-instance@boai-skills` |
| 🔒 mac-wechat-anti-recall | `/plugin install mac-wechat-anti-recall@boai-skills` |

装完执行 `/reload-plugins` 让当前会话立即生效（或重启 Claude Code）。要卸载或管理已装插件，打开 `/plugin` 面板即可。

## 收录内容

### ⚙️ 自动运行（hook，无需触发词）

| 插件 | 说明 | 启用方式 |
|------|------|----------|
| 📊 **claude-token-tracker** | 每轮回答结束自动显示 token 用量：当前对话 / 今日 / 本月 / 历史全部，各含明细+合计 | 装完重启即自动运行 |

### 🌐 通用 / 内容创作（技能，提到触发词时启用）

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 📝 **boai-article-writer** | 微信公众号文章全流程：选题调研→文章撰写→配图→封面设计→发布检查 | `写文章` `公众号文章` `写一篇文章` |
| 🎬 **boai-film-review** | 公众号"博爱光影"影评全流程：选题调研→分类归档→撰写→配图→封面设计→发布检查 | `写影评` `公众号影评` `博爱光影` |

### ✈️ 出行（技能，提到触发词时启用）

| 技能 | 说明 | 触发词 |
|------|------|--------|
| ✈️ **boai-travel-guide** | 旅游攻略生成：行程编排 + 联网调研（路线/充电/景点/美食/住宿/预算）+ 精排版 PDF 交付，支持电车自驾充电规划 | `旅游攻略` `自驾` `周末去哪玩` `X日游` `行程规划` |

### 🍜 城市美食（技能，提到触发词时启用）

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 🍜 **boai-city-food** | 一句话搜一座城市最好吃的美食：按区域整理，星级推荐 + 店名/地址/菜价/人均，PDF 交付 | `美食推荐` `有什么好吃的` `必吃` `探店` |

### 🪟 Windows

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 🧹 **sogou-ad-killer** | 扫描所有搜狗产品，手动勾选关闭广告，一键全禁预设 | `去搜狗广告` `sogou ad killer` `管理搜狗` |
| 🔧 **360-cleaner** | 扫描系统所有360产品，手动勾选卸载，含快捷预设 | `清理360` `卸载360` `管理360` |

### 🍎 macOS

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 💬 **mac-wechat-dual-instance** | 微信双开/多开，无需禁SIP，原生Apple Silicon | `微信双开` `微信分身` `wechat dual` |
| 🔒 **mac-wechat-anti-recall** | 微信防撤回，全消息类型支持，附带去日志/去更新 | `微信防撤回` `anti recall` `anti revoke` |

## 版本

**对外只有一个版本号**（下面的「对外发布版本」）——由仓库根的 `.claude-plugin/plugin.json` 决定，也是驱动自动更新的唯一依据。各技能的版本号属于**内部记录**，不影响用户看到或拿到的版本。

> 为什么不做「每个技能一个版本」？官方规则里 marketplace 条目的 `version` 会被 `plugin.json` **静默覆盖**（`claude plugin validate` 会警告），而本仓库所有技能条目都指向同一份清单 —— 一个市场同一时刻只对外提供一个版本。

<!-- versions:start -->

**对外发布版本：`1.6.0`** — 用户安装/更新时看到的版本，也是驱动更新的唯一版本号。
整包与 8 个技能条目共用它；发版时改它，用户下次自动收到更新。

独立插件（拥有自己的 `plugin.json`，版本独立生效）：

| 插件 | 版本 |
| --- | --- |
| `claude-token-tracker` | 1.0.1 |

各技能内部版本（仅记录该技能自身迭代，**不影响用户看到的版本**）：

| 技能 | 内部版本 |
| --- | --- |
| `360-cleaner` | 1.0.0 |
| `boai-article-writer` | 2.3.0 |
| `boai-city-food` | 1.0.0 |
| `boai-film-review` | 2.4.0 |
| `boai-travel-guide` | 1.0.0 |
| `mac-wechat-anti-recall` | 1.0.0 |
| `mac-wechat-dual-instance` | 1.0.0 |
| `sogou-ad-killer` | 1.0.0 |

<!-- versions:end -->

**递增规则**

| 改动 | 版本动作 | 例子 |
|------|----------|------|
| 新增技能、大改流程 | minor +1 | 1.6.0 → 1.7.0 |
| 修 bug、补细节 | patch +1 | 1.7.0 → 1.7.1 |
| 破坏性变更（改目录/触发词不兼容） | major +1 | 1.7.1 → 2.0.0 |

**改版本号（别手工改，用脚本）**

```bash
./scripts/bump-version.sh list                                  # 查看所有版本
./scripts/bump-version.sh release 1.7.0                         # 发版：改对外版本并同步 README
./scripts/bump-version.sh skill mac-wechat-anti-recall 1.0.1     # 记一次内部技能版本（对外不变）
./scripts/bump-version.sh plugin claude-token-tracker 1.1.0      # 独立插件自己的版本
./scripts/bump-version.sh sync                                  # README 版本区与源头不一致时，补一次
```

两个要点：

- **`release` 是唯一让用户拿到新版本的动作** —— 它改 `plugin.json` 的 version（Claude Code 用这个值判断要不要更新）。只 push 代码不改 version，用户会一直停在旧版本。
- **`skill` 只动内部记录**，用户完全无感。

## 目录结构

```plaintext
boai-skills/
├── .claude-plugin/
│   ├── marketplace.json      # 市场清单：整包 + 各技能/插件可单独安装
│   └── plugin.json           # 整包 plugin 清单（8 个触发式技能）· **对外版本号在这里**
├── plugins/
│   └── claude-token-tracker/ # 自动 token 统计（Stop hook 插件）
│       ├── .claude-plugin/plugin.json
│       ├── hooks/hooks.json
│       └── scripts/token-usage-summary.py
├── skills/                   # 触发式技能
│   ├── boai-article-writer/SKILL.md
│   ├── boai-film-review/SKILL.md
│   ├── boai-travel-guide/
│   │   ├── SKILL.md
│   │   ├── assets/guide_template.html   # 攻略 PDF 精排版模板
│   │   └── scripts/html2pdf.sh          # 无头 Chrome 转 PDF
│   ├── sogou-ad-killer/SKILL.md
│   ├── 360-cleaner/SKILL.md
│   ├── mac-wechat-dual-instance/SKILL.md
│   └── mac-wechat-anti-recall/SKILL.md
├── scripts/                  # 维护脚本
│   ├── sogou_ad_killer.ps1          # 搜狗去广告（Windows PowerShell）
│   └── bump-version.sh              # 版本号工具（发版 / 内部技能版本 / README 同步）
├── README.md
└── LICENSE
```

## 许可

MIT License

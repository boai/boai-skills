---
name: api-to-swift-model
description: 把 OpenAPI / Swagger 文档或 JSON 响应样本转换成 Swift Codable 模型、Mock 数据和可选的 URLSession 请求骨架，自动处理 snake_case、可选性、枚举和嵌套类型，并用 swiftc 做编译校验。当用户说「接口转模型」「JSON 转 Swift」「生成 Codable」「OpenAPI 生成模型」「Swagger 转 Swift」「写模型类」「Mock 数据」「联调准备」时使用。适用于 iOS / macOS 的 Swift 项目。
version: 1.0.0
triggers:
  - 接口转模型
  - JSON 转 Swift
  - 生成 Codable
  - OpenAPI
  - Swagger
  - Mock 数据
  - 联调
---

# 接口文档转 Swift 模型

## 解决什么问题

联调前写模型是纯体力活：字段多、嵌套深、`snake_case` 要手写 `CodingKeys`，漏一个字段就解析失败，类型写错要跑起来才发现。

这个 skill 的原则是：**结构和字段由脚本确定性生成，AI 只做命名优化和业务注释。** 不依赖模型「凭记忆写代码」，所以不会凭空多字段、少字段或写错类型；生成的每个文件都过一遍 `swiftc -typecheck`，保证类型正确、可编译。

## 何时使用

- 拿到后端 OpenAPI / Swagger 文档，要生成 iOS 模型
- 只有接口返回的 JSON 样本，没有文档
- 需要 Mock 数据做本地调试或 UI 预览
- 联调前想先把模型和请求骨架搭好

**不适用**：接口还没定（模型一定会变）；只需要解析一层简单字段（手写更快）；项目使用代码生成工具（如 Sourcery）且已有固定模板。

## 工作流

### 第 1 步：判断输入类型

| 输入 | 识别方式 | 处理 |
|------|----------|------|
| OpenAPI 3 / Swagger 2 | 文件里有 `openapi` / `swagger` 字段 | 脚本直接生成全部 schema |
| JSON 响应样本 | 一段合法 JSON | 从样本推断结构 |
| Postman 集合 | 集合 JSON | 从 `response` 示例中提取 body，另存为样本 JSON |
| 飞书 / 在线接口文档 | 文档页面 | 让用户提供示例响应 JSON，或导出 OpenAPI 文件 |
| 只有字段表格 | Markdown / Excel | 先让用户补一份示例 JSON，再走样本模式 |

**强烈建议提供 2 份以上 JSON 样本**（成功、空数据、异常），脚本会对比多份样本推断哪些字段是可选、哪些可能为 null。只有一份样本时，所有字段都会按必填处理，接口一变就可能解析失败。

### 第 2 步：运行生成脚本

**OpenAPI / Swagger：**

```bash
# <skill目录> 换成实际路径；安装后通常是 ~/.claude/skills/api-to-swift-model
python3 <skill目录>/scripts/generate_swift.py \
  --input api.json \
  --out Models.swift \
  --mock-out Mock.json \
  --request-skeleton
```

**JSON 样本（可多个）：**

```bash
python3 <skill目录>/scripts/generate_swift.py \
  --input sample1.json sample2.json \
  --root-name VehicleDetail \
  --out Models.swift \
  --mock-out Mock.json
```

参数说明：

| 参数 | 说明 |
|------|------|
| `--input` | OpenAPI 文件，或一个/多个 JSON 样本 |
| `--out` | 输出 Swift 文件，默认 `Models.swift` |
| `--mock-out` | Mock JSON 路径，默认与 Swift 文件同名 + `.Mock.json` |
| `--root-name` | JSON 模式下的根类型名；OpenAPI 模式下可指定优先输出的 schema |
| `--date-as-date` | `date-time` 映射为 `Date`（默认 `String`） |
| `--request-skeleton` | 为 OpenAPI 的 GET 接口生成 URLSession 请求骨架 |
| `--force` | 输出文件已存在时覆盖 |

支持的格式：OpenAPI 3.x、Swagger 2.0（`definitions`）、JSON、YAML（需 PyYAML）。

### 第 3 步：检查生成结果

脚本负责「不漏」，这一步负责「好用」。逐项检查：

1. **命名**：`plate_number` → `plateNumber`，`is_on` → `isOn`，是否符合团队规范
2. **可选性**：接口可能不返回的字段是否带 `?`；只有一份样本时尤其要人工确认
3. **枚举**：状态类字段是否生成了 `String` 枚举；如果后端会新增枚举值，考虑改回 `String` 并加兜底
4. **空数组**：样本里是空数组的字段，脚本默认推断为 `[String]`，需要按实际类型改
5. **未知类型**：脚本对无法识别的类型会兜底成 `String?`，要人工核对
6. **嵌套命名**：`VehicleDetailDataOwner` 这类名字是否过长，可按团队习惯简化
7. **CodingKeys**：只在下划线/特殊字符字段上生成；确认没有漏

**修改原则**：只改命名、注释、访问控制、是否可选；**不要重写整个结构**。字段增删一定要回到脚本，用新的样本重新生成，避免手工改出偏差。

### 第 4 步：编译校验

```bash
bash <skill目录>/scripts/verify_swift.sh Models.swift
```

必须出现 `✅ Swift 编译检查通过`（脚本执行 `swiftc -typecheck`，能发现未定义类型、协议不满足等类型错误）。如果失败，把错误贴出来修复，不要交付未编译的模型文件。

### 第 5 步：接入项目

- 把 `Models.swift` 加入 target
- `Mock.json` 用于单元测试、SwiftUI Preview、本地假数据
- 请求骨架是**示例**：URLSession 版本是参考实现，生产使用请按项目网络层规范替换，并确认路径参数编码符合后端约定
- 如果项目统一用 `Date`，加 `--date-as-date` 并配置 `JSONDecoder.dateDecodingStrategy`

## 类型映射规则

| JSON / OpenAPI | Swift |
|----------------|-------|
| `string` | `String` |
| `string` + `format: date-time` | `String`（`--date-as-date` 时为 `Date`） |
| `integer` | `Int` |
| `number` | `Double` |
| `boolean` | `Bool` |
| `array` | `[Element]` |
| `object` | 嵌套 `struct` |
| `null` / 非必填 | `Optional`（`?`） |
| `enum`（字符串） | `enum Name: String, Codable` |
| `additionalProperties` | `[String: T]` |
| 无法识别 | `String?`（需人工核对） |

## 可选性判断

- **OpenAPI**：在 `required` 列表里且非 `nullable` → 非可选；否则可选
- **多份 JSON 样本**：所有样本都出现且都不为 null → 非可选；缺一次或为 null → 可选
- **单份 JSON 样本**：值为 null → 可选；其余按必填处理（**需要人工复核**）

## 无本地环境时（飞书 Aily / 纯对话）

1. 让用户粘贴 JSON 样本或 OpenAPI 片段
2. 按同样的命名与类型规则手工输出 Swift 代码
3. 明确告诉用户：**这是降级模式，没有经过 swiftc 校验**，建议回到本地用脚本重新生成一遍
4. 输出时保持字段顺序与源数据一致，并补齐 `CodingKeys`

## 验证方式

```bash
# <skill目录> 换成实际路径；安装后通常是 ~/.claude/skills/api-to-swift-model

# OpenAPI 示例
python3 <skill目录>/scripts/generate_swift.py \
  --input <skill目录>/examples/openapi-example.json \
  --out /tmp/Models.swift \
  --mock-out /tmp/Mock.json \
  --request-skeleton
bash <skill目录>/scripts/verify_swift.sh /tmp/Models.swift

# JSON 样本示例（两份样本，观察 snake_case、嵌套、null、可选字段推断）
python3 <skill目录>/scripts/generate_swift.py \
  --input <skill目录>/examples/vehicle-response.json <skill目录>/examples/vehicle-response-partial.json \
  --root-name VehicleDetail \
  --out /tmp/ModelsJSON.swift
bash <skill目录>/scripts/verify_swift.sh /tmp/ModelsJSON.swift
```

示例 OpenAPI 包含 5 个 schema、枚举、嵌套对象、`allOf` 继承、路径参数和查询参数，正常应生成 10 个以上类型定义，并且编译检查通过。

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 让 AI 凭文档手写整个模型 | 用脚本生成，AI 只改命名和注释 |
| 只给一份样本就判定字段必填 | 多给几份样本，或人工确认可选性 |
| 生成后不编译就交付 | 必须跑 `verify_swift.sh` |
| 手工增删字段 | 回到脚本，用新样本重新生成 |
| 把枚举写死 | 后端可能新增值，评估是否用 `String` + 兜底 |
| 忽略空数组和 null | 这两类最容易出现类型错误，逐项核对 |
| 请求骨架直接用于生产 | 骨架是示例，按项目网络层规范替换 |
| `Date` 字段没配解码策略 | 用 `--date-as-date` 时同步配置 `JSONDecoder` |

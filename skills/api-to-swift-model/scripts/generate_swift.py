#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 OpenAPI/Swagger 文档或 JSON 响应样本转换为 Swift Codable 模型 + Mock 数据。

设计原则：结构与字段由脚本确定性生成，AI 只负责命名优化和业务注释，
避免「AI 凭空写模型导致字段丢失 / 类型错误」。
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

SWIFT_KEYWORDS = {
    "associatedtype", "class", "deinit", "enum", "extension", "fileprivate",
    "func", "import", "init", "inout", "internal", "let", "open", "operator",
    "private", "protocol", "public", "rethrows", "static", "struct", "subscript",
    "typealias", "var", "break", "case", "continue", "default", "defer", "do",
    "else", "fallthrough", "for", "guard", "if", "in", "repeat", "return",
    "switch", "where", "while", "as", "catch", "false", "is", "nil", "super",
    "self", "Self", "throw", "throws", "true", "try", "weak", "unowned",
    "override", "final", "lazy", "mutating", "nonmutating", "convenience",
    "required", "dynamic", "optional", "indirect", "Any", "Type",
}


def die(msg):
    print("错误：%s" % msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- 命名工具

def split_words(name):
    name = re.sub(r"[^0-9A-Za-z]+", "_", str(name)).strip("_")
    if not name:
        return []
    if "_" in name:
        return [p for p in name.split("_") if p]
    # HTTPStatus -> HTTP, Status
    parts = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+", name)
    return parts or [name]


def lower_camel(name, fallback="value"):
    words = split_words(name)
    if not words:
        return fallback
    result = words[0].lower() + "".join(w[:1].upper() + w[1:].lower() if w.isupper() else w[:1].upper() + w[1:]
                                        for w in words[1:])
    if result[0].isdigit():
        result = fallback + result
    if result in SWIFT_KEYWORDS:
        result += "Value"
    return result


def upper_camel(name, fallback="Model"):
    camel = lower_camel(name, fallback=fallback)
    result = camel[:1].upper() + camel[1:]
    if not result or result[0].isdigit():
        result = fallback + result
    if result in SWIFT_KEYWORDS:
        result += "Model"
    return result


def singularize(word):
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("ses") and len(word) > 3:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word + "Item"


# ---------------------------------------------------------------- Schema 统一表示
# {"type": "object|array|string|integer|number|boolean|any|ref",
#  "properties": {name: schema}, "required": set(), "items": schema,
#  "enum": [...], "ref": "Name", "format": "...", "nullable": bool,
#  "additional": schema|None, "example": any}

def from_openapi(schema, nullable=False):
    if not isinstance(schema, dict):
        return {"type": "any", "nullable": nullable}
    if "$ref" in schema:
        ref = schema["$ref"].rsplit("/", 1)[-1]
        return {"type": "ref", "ref": ref, "nullable": nullable}

    nullable = bool(schema.get("nullable", nullable))
    if "allOf" in schema:
        merged = {"type": "object", "properties": {}, "required": set(), "nullable": nullable}
        for sub in schema["allOf"]:
            sub_schema = from_openapi(sub, nullable)
            if sub_schema.get("type") == "ref":
                merged.setdefault("_refs", []).append(sub_schema["ref"])
                continue
            merged["properties"].update(sub_schema.get("properties", {}))
            merged["required"].update(sub_schema.get("required", set()))
        return merged

    t = schema.get("type")
    if t is None:
        if "properties" in schema:
            t = "object"
        elif "items" in schema:
            t = "array"
        elif "enum" in schema:
            t = "string"
        else:
            t = "any"

    result = {"type": t, "nullable": nullable, "format": schema.get("format"), "example": schema.get("example")}

    if t == "object":
        result["properties"] = {k: from_openapi(v) for k, v in (schema.get("properties") or {}).items()}
        result["required"] = set(schema.get("required") or [])
        if isinstance(schema.get("additionalProperties"), dict):
            result["additional"] = from_openapi(schema["additionalProperties"])
    elif t == "array":
        result["items"] = from_openapi(schema.get("items") or {})
    elif "enum" in schema:
        result["enum"] = schema["enum"]
    return result


def resolve_allof(schema, schemas):
    """把 allOf（含 $ref）合并成单一 object schema。"""
    if not isinstance(schema, dict) or "allOf" not in schema:
        return schema
    base = {k: v for k, v in schema.items() if k != "allOf"}
    properties = dict(base.get("properties") or {})
    required = set(base.get("required") or [])
    for sub in schema["allOf"]:
        if not isinstance(sub, dict):
            continue
        if "$ref" in sub:
            target = schemas.get(sub["$ref"].rsplit("/", 1)[-1]) or {}
            target = resolve_allof(target, schemas)
            properties.update(target.get("properties") or {})
            required.update(target.get("required") or [])
        else:
            sub = resolve_allof(sub, schemas)
            properties.update(sub.get("properties") or {})
            required.update(sub.get("required") or [])
    base["type"] = "object"
    base["properties"] = properties
    base["required"] = list(required)
    return base


def deep_resolve_allof(schema, schemas, depth=0):
    """递归解析嵌套结构里的 allOf。"""
    if not isinstance(schema, dict) or depth > 12:
        return schema
    schema = resolve_allof(schema, schemas)
    if isinstance(schema.get("properties"), dict):
        schema["properties"] = {k: deep_resolve_allof(v, schemas, depth + 1)
                                for k, v in schema["properties"].items()}
    if isinstance(schema.get("items"), dict):
        schema["items"] = deep_resolve_allof(schema["items"], schemas, depth + 1)
    return schema


def merge_schema(a, b):
    """合并两份样本推断出的 schema，用于判定可选字段。"""
    if a is None:
        return b
    if b is None:
        return a
    ta, tb = a.get("type"), b.get("type")
    if {ta, tb} == {"integer", "number"}:
        return {"type": "number", "nullable": a.get("nullable") or b.get("nullable")}
    if ta != tb:
        return {"type": "any", "nullable": True}
    if ta == "object":
        keys = list(a.get("properties", {}).keys())
        for key in b.get("properties", {}):
            if key not in keys:
                keys.append(key)
        props = {}
        for key in keys:
            props[key] = merge_schema(a.get("properties", {}).get(key), b.get("properties", {}).get(key))
        required = set(a.get("required", set())) & set(b.get("required", set()))
        required = {k for k in required if k in a["properties"] and k in b["properties"]
                    and not a["properties"][k].get("nullable") and not b["properties"][k].get("nullable")}
        return {"type": "object", "properties": props, "required": required}
    if ta == "array":
        return {"type": "array", "items": merge_schema(a.get("items"), b.get("items"))}
    return {"type": ta, "nullable": a.get("nullable") or b.get("nullable"), "format": a.get("format")}


def infer_schema(value):
    if value is None:
        return {"type": "any", "nullable": True}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, list):
        item = None
        for element in value:
            item = merge_schema(item, infer_schema(element))
        # 空数组无法推断元素类型，默认按 String，生成后请按实际接口调整
        return {"type": "array", "items": item or {"type": "string"}}
    if isinstance(value, dict):
        return {
            "type": "object",
            "properties": {k: infer_schema(v) for k, v in value.items()},
            "required": {k for k, v in value.items() if v is not None},
        }
    return {"type": "any", "nullable": True}


# ---------------------------------------------------------------- Swift 生成

class SwiftGenerator:
    def __init__(self, date_as_date=False, access="let"):
        self.definitions = {}
        self.emitting = set()
        self.date_as_date = date_as_date
        self.access = access

    def register(self, name, code):
        if name in self.definitions:
            if self.definitions[name] != code:
                print("警告：类型名冲突 %s，保留首次定义；请检查 schema 命名" % name, file=sys.stderr)
            return
        self.definitions[name] = code

    def emit_type(self, schema, name_hint, force_name=False):
        if schema is None:
            return "String?"
        t = schema.get("type", "any")
        optional = "?" if schema.get("nullable") else ""

        if t == "ref":
            ref = schema["ref"]
            return ref + optional

        if t == "array":
            item = schema.get("items") or {"type": "any"}
            item_name = upper_camel(singularize(name_hint), fallback="Item")
            inner = self.emit_type(item, item_name, force_name=force_name)
            return "[%s]%s" % (inner, optional)

        if t == "object":
            if schema.get("additional") is not None:
                return "[String: %s]%s" % (self.emit_type(schema["additional"], name_hint + "Value"), optional)
            struct_name = upper_camel(name_hint)
            if struct_name not in self.emitting:
                self.emitting.add(struct_name)
                fields = []
                coding_keys = []
                needs_keys = False
                for raw_key, prop_schema in (schema.get("properties") or {}).items():
                    prop_name = lower_camel(raw_key)
                    prop_type = self.emit_type(prop_schema, struct_name + upper_camel(raw_key))
                    is_required = raw_key in schema.get("required", set()) and not prop_schema.get("nullable")
                    if not is_required and not prop_type.endswith("?"):
                        prop_type += "?"
                    fields.append("    %s %s: %s" % (self.access, prop_name, prop_type))
                    coding_keys.append((prop_name, raw_key))
                    if prop_name != raw_key:
                        needs_keys = True
                if not fields:
                    fields = ["    // 空对象"]
                body = "struct %s: Codable {\n%s\n" % (struct_name, "\n".join(fields))
                if needs_keys:
                    keys = []
                    for prop_name, raw_key in coding_keys:
                        if prop_name == raw_key:
                            keys.append("        case %s" % prop_name)
                        else:
                            keys.append('        case %s = "%s"' % (prop_name, raw_key))
                    body += "\n    enum CodingKeys: String, CodingKey {\n%s\n    }\n" % "\n".join(keys)
                body += "}\n"
                self.register(struct_name, body)
                self.emitting.discard(struct_name)
            return struct_name + optional

        if t == "string" and schema.get("enum"):
            enum_name = upper_camel(name_hint)
            if enum_name not in self.emitting:
                self.emitting.add(enum_name)
                cases = []
                used = set()
                for value in schema["enum"]:
                    case_name = lower_camel(str(value), fallback="value")
                    if case_name in used:
                        case_name += str(len(used))
                    used.add(case_name)
                    cases.append('    case %s = "%s"' % (case_name, str(value).replace('"', '\\"')))
                if cases:
                    self.register(enum_name, "enum %s: String, Codable {\n%s\n}\n" % (enum_name, "\n".join(cases)))
                self.emitting.discard(enum_name)
            return enum_name + optional

        mapping = {"string": "String", "integer": "Int", "number": "Double", "boolean": "Bool"}
        if t == "any":
            return "String?"  # 未知类型按字符串兜底并标记可选
        base = mapping.get(t, "String")
        if t == "string" and schema.get("format") == "date-time" and self.date_as_date:
            base = "Date"
        return base + optional

    def render(self, root_schema, root_name, header_comment):
        root_type = self.emit_type(root_schema, root_name, force_name=True)
        chunks = [header_comment, "import Foundation", ""]
        for name in sorted(self.definitions):
            chunks.append(self.definitions[name])
        return "\n".join(chunks).rstrip() + "\n", root_type


def load_document(path):
    if not os.path.isfile(path):
        die("文件不存在：%s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if path.lower().endswith((".yaml", ".yml")):
        if yaml is None:
            die("读取 YAML 需要 PyYAML，请先运行: python3 -m pip install --user pyyaml")
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            die("YAML 格式错误：%s\n%s" % (path, exc))
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        if yaml is None:
            die("JSON 解析失败：%s" % exc)
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as yaml_exc:
            die("YAML 格式错误：%s\n%s" % (path, yaml_exc))


def is_openapi(doc):
    return isinstance(doc, dict) and ("openapi" in doc or "swagger" in doc) and ("paths" in doc or "components" in doc or "definitions" in doc)


def openapi_schemas(doc):
    if "components" in doc and isinstance(doc["components"], dict):
        return doc["components"].get("schemas") or {}
    return doc.get("definitions") or {}


def openapi_root_schema(doc, schemas, preferred=None):
    if preferred and preferred in schemas:
        return {"type": "ref", "ref": preferred}, preferred
    if len(schemas) == 1:
        name = next(iter(schemas))
        return {"type": "ref", "ref": name}, name
    # 优先取第一个成功响应引用的 schema，其次取字段最多的
    for methods in (doc.get("paths") or {}).values():
        if not isinstance(methods, dict):
            continue
        for operation in methods.values():
            if not isinstance(operation, dict):
                continue
            for code in ("200", "201"):
                response = (operation.get("responses") or {}).get(code)
                if not isinstance(response, dict):
                    continue
                if "content" in response:
                    media = response["content"].get("application/json") or {}
                    ref = (media.get("schema") or {}).get("$ref")
                else:
                    ref = (response.get("schema") or {}).get("$ref")
                if ref:
                    name = ref.rsplit("/", 1)[-1]
                    if name in schemas:
                        return {"type": "ref", "ref": name}, name
    name = max(schemas, key=lambda k: len((schemas[k] or {}).get("properties") or {}))
    return {"type": "ref", "ref": name}, name


def build_generator(doc):
    """返回 (generator, root_schema, root_name, schema_map)，并把所有命名 schema 注册进去。"""
    gen = SwiftGenerator()
    schemas = openapi_schemas(doc)
    for name, schema in schemas.items():
        normalized = from_openapi(schema)
        gen.emit_type(normalized, name, force_name=True)
    root_schema, root_name = openapi_root_schema(doc, schemas)
    return gen, root_schema, root_name, schemas


def mock_from_schema(schema, schemas, depth=0):
    if schema is None or depth > 8:
        return None
    if schema.get("example") is not None:
        return schema["example"]
    if schema.get("type") == "ref":
        target = schemas.get(schema["ref"]) or {}
        return mock_from_schema(from_openapi(target), schemas, depth + 1)
    t = schema.get("type")
    if t == "object":
        return {k: mock_from_schema(v, schemas, depth + 1) for k, v in (schema.get("properties") or {}).items()}
    if t == "array":
        item = mock_from_schema(schema.get("items"), schemas, depth + 1)
        return [item] if item is not None else []
    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return False
    if t == "string" and schema.get("enum"):
        return schema["enum"][0]
    fmt = schema.get("format")
    if fmt == "date-time":
        return "2026-01-01T00:00:00Z"
    if fmt == "date":
        return "2026-01-01"
    return "string"


def request_skeleton(doc, schemas, gen):
    paths = doc.get("paths") or {}
    base_url = "https://api.example.com"
    servers = doc.get("servers") or []
    if servers and isinstance(servers, list) and servers[0].get("url"):
        base_url = servers[0]["url"].rstrip("/")

    functions = []
    used_names = set()
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() != "get" or not isinstance(operation, dict):
                continue
            op_name = operation.get("operationId") or (method + "_" + path)
            func_name = lower_camel(op_name, fallback="request")
            if func_name in used_names:
                func_name += str(len(used_names))
            used_names.add(func_name)

            # 响应类型
            responses = operation.get("responses") or {}
            success = responses.get("200") or responses.get("201") or {}
            if "content" in success:
                media = success["content"].get("application/json") or next(iter(success["content"].values()), {})
                resp_schema = from_openapi(media.get("schema") or {})
            else:
                resp_schema = from_openapi(success.get("schema") or {})
            resp_type = gen.emit_type(resp_schema, func_name + "Response")

            # 路径参数
            params = operation.get("parameters") or []
            path_params = []
            query_params = []
            for p in params:
                if "$ref" in p:
                    continue
                p_schema = from_openapi(p.get("schema") or {"type": "string"})
                p_type = gen.emit_type(p_schema, func_name + upper_camel(p.get("name", "param")))
                p_name = lower_camel(p.get("name", "param"))
                if p.get("in") == "path":
                    path_params.append((p_name, p_type, p["name"]))
                elif p.get("in") == "query":
                    query_params.append((p_name, p_type, p["name"], bool(p.get("required"))))

            url_path = path
            path_encoding_lines = []
            for p_name, _, raw_name in path_params:
                encoded_name = p_name + "Path"
                path_encoding_lines.append(
                    '        let %s = String(describing: %s).addingPercentEncoding(withAllowedCharacters: .urlPathAllowed.subtracting(CharacterSet(charactersIn: "/"))) ?? ""'
                    % (encoded_name, p_name))
                url_path = url_path.replace("{%s}" % raw_name, "\\(%s)" % encoded_name)

            args = []
            for p_name, p_type, _ in path_params:
                args.append("%s: %s" % (p_name, p_type.rstrip("?")))
            for p_name, p_type, _, required in query_params:
                args.append("%s: %s" % (p_name, p_type.rstrip("?") if required else p_type.rstrip("?") + "?"))
            signature = ", ".join(args + ["completion: @escaping (Result<%s, Error>) -> Void" % resp_type.rstrip("?")])

            lines = []
            lines.append("    static func %s(%s) {" % (func_name, signature))
            lines.extend(path_encoding_lines)
            if query_params:
                lines.append('        guard var components = URLComponents(string: "%s%s") else {' % (base_url, url_path))
                lines.append("            completion(.failure(URLError(.badURL)))")
                lines.append("            return")
                lines.append("        }")
                lines.append("        var queryItems: [URLQueryItem] = []")
                for p_name, p_type, raw_name, required in query_params:
                    if required:
                        lines.append('        queryItems.append(URLQueryItem(name: "%s", value: String(describing: %s)))' % (raw_name, p_name))
                    else:
                        lines.append("        if let %s = %s {" % (p_name, p_name))
                        lines.append('            queryItems.append(URLQueryItem(name: "%s", value: String(describing: %s)))' % (raw_name, p_name))
                        lines.append("        }")
                lines.append("        components.queryItems = queryItems.isEmpty ? nil : queryItems")
                lines.append("        guard let url = components.url else {")
                lines.append("            completion(.failure(URLError(.badURL)))")
                lines.append("            return")
                lines.append("        }")
            else:
                lines.append('        guard let url = URL(string: "%s%s") else {' % (base_url, url_path))
                lines.append("            completion(.failure(URLError(.badURL)))")
                lines.append("            return")
                lines.append("        }")
            lines.append("        URLSession.shared.dataTask(with: url) { data, _, error in")
            lines.append("            if let error = error {")
            lines.append("                completion(.failure(error))")
            lines.append("                return")
            lines.append("            }")
            lines.append("            guard let data = data else {")
            lines.append("                completion(.failure(URLError(.badServerResponse)))")
            lines.append("                return")
            lines.append("            }")
            lines.append("            do {")
            lines.append("                let value = try JSONDecoder().decode(%s.self, from: data)" % resp_type.rstrip("?"))
            lines.append("                completion(.success(value))")
            lines.append("            } catch {")
            lines.append("                completion(.failure(error))")
            lines.append("            }")
            lines.append("        }.resume()")
            lines.append("    }")
            functions.append("\n".join(lines))

    if not functions:
        return ""
    return "\n// MARK: - 请求骨架（示例，请按项目网络层规范调整）\n\nenum GeneratedAPI {\n%s\n}\n" % "\n\n".join(functions)


def main():
    parser = argparse.ArgumentParser(description="OpenAPI / JSON 转 Swift Codable 模型")
    parser.add_argument("--input", nargs="+", required=True,
                        help="OpenAPI/Swagger 文件，或一个/多个 JSON 响应样本")
    parser.add_argument("--out", default="Models.swift", help="输出 Swift 文件")
    parser.add_argument("--mock-out", default="", help="Mock JSON 输出路径，默认与 Swift 同目录")
    parser.add_argument("--root-name", default="", help="JSON 样本模式下的根类型名，默认取文件名")
    parser.add_argument("--date-as-date", action="store_true", help="date-time 映射为 Date 而不是 String")
    parser.add_argument("--request-skeleton", action="store_true", help="为 OpenAPI 的 GET 接口生成 URLSession 请求骨架")
    parser.add_argument("--force", action="store_true", help="输出文件已存在时覆盖")
    args = parser.parse_args()

    documents = [(path, load_document(path)) for path in args.input]
    first_path, first_doc = documents[0]

    skeleton = ""
    if is_openapi(first_doc):
        schemas = openapi_schemas(first_doc)
        # 先合并 allOf，避免继承来的字段丢失
        for name in list(schemas.keys()):
            schemas[name] = deep_resolve_allof(schemas[name], schemas)
        gen = SwiftGenerator(date_as_date=args.date_as_date)
        for name, schema in schemas.items():
            gen.emit_type(from_openapi(schema), name, force_name=True)
        root_schema, root_name = openapi_root_schema(first_doc, schemas, args.root_name or None)
        root_type = gen.emit_type(root_schema, root_name)
        mock = mock_from_schema(root_schema, schemas)
        if args.request_skeleton:
            skeleton = request_skeleton(first_doc, schemas, gen)
        root_for_render = root_schema
    else:
        merged = None
        for _, doc in documents:
            merged = merge_schema(merged, infer_schema(doc))
        gen = SwiftGenerator(date_as_date=args.date_as_date)
        root_name = args.root_name or upper_camel(os.path.splitext(os.path.basename(first_path))[0], fallback="Model")
        root_type = gen.emit_type(merged, root_name, force_name=True)
        mock = documents[0][1]
        root_for_render = merged

    header = "// Generated by api-to-swift-model\n// Source: %s\n// 字段与类型由脚本确定性生成；命名可在生成后微调。" % ", ".join(os.path.basename(p) for p, _ in documents)
    code, _ = gen.render(root_for_render, root_name, header)
    code += skeleton

    mock_path = args.mock_out or os.path.splitext(args.out)[0] + ".Mock.json"
    for path in (args.out, mock_path if mock is not None else None):
        if path and os.path.exists(path) and not args.force:
            die("输出文件已存在：%s（确认要覆盖请加 --force）" % path)

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(code)

    if mock is not None:
        with open(mock_path, "w", encoding="utf-8") as fh:
            json.dump(mock, fh, ensure_ascii=False, indent=2)

    print("已生成: %s" % os.path.abspath(args.out))
    if mock is not None:
        print("Mock: %s" % os.path.abspath(mock_path))
    print("根类型: %s，共生成 %d 个类型定义。" % (root_type.rstrip("?"), len(gen.definitions)))


if __name__ == "__main__":
    main()

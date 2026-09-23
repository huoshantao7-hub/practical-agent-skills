"""Validate and assemble prompt assets offline; no model or network calls."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys

NAME = re.compile(r"[a-z][a-z0-9_]*\Z")
SLOT = re.compile(r"\{\{\s*([a-z][a-z0-9_]*)\s*\}\}")
TOP = {"schema_version", "title", "goal", "template", "variables", "constraints",
       "output_contract", "references", "conflicts", "tests"}


def validate(document: object) -> list[str]:
    """Return field-level contract errors; never echo input values."""
    errors: list[str] = []

    def obj(value: object, fields: set[str], path: str) -> bool:
        if not isinstance(value, dict):
            errors.append(f"{path}: expected object")
            return False
        if set(value) != fields:
            errors.append(f"{path}: missing or unknown fields")
            return False
        return True

    def string(value: object, path: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path}: expected nonempty string")
            return False
        return True

    def strings(value: object, path: str, nonempty: bool = False) -> bool:
        if not isinstance(value, list) or (nonempty and not value):
            errors.append(f"{path}: expected {'nonempty ' if nonempty else ''}list")
            return False
        for index, item in enumerate(value):
            string(item, f"{path}[{index}]")
        return True

    if not obj(document, TOP, "document"):
        return errors
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        errors.append("schema_version: expected integer 1")
    for field in ("title", "goal", "template"):
        string(document[field], field)
    for field in ("constraints", "output_contract"):
        strings(document[field], field, nonempty=True)

    variables = document["variables"]
    if not isinstance(variables, dict):
        errors.append("variables: expected object")
    else:
        for index, (name, spec) in enumerate(variables.items()):
            path = f"variables item {index}"
            if not isinstance(name, str) or not NAME.fullmatch(name):
                errors.append(f"{path}: invalid variable name")
            if obj(spec, {"description", "example"}, path):
                string(spec["description"], path + ".description")
                string(spec["example"], path + ".example")
        if isinstance(document["template"], str):
            template = document["template"]
            used = set(SLOT.findall(template))
            if used != set(variables):
                errors.append("template: declared variables and slots must match")
            remainder = SLOT.sub("", template)
            if "{{" in remainder or "}}" in remainder:
                errors.append("template: malformed slot or reserved double braces")

    references = document["references"]
    if not isinstance(references, list):
        errors.append("references: expected list")
    else:
        seen: set[str] = set()
        for i, reference in enumerate(references):
            path = f"references[{i}]"
            if not obj(reference, {"id", "source", "status", "use", "excluded"}, path):
                continue
            if string(reference["id"], path + ".id"):
                if reference["id"] in seen:
                    errors.append(path + ".id: duplicate identifier")
                seen.add(reference["id"])
            string(reference["source"], path + ".source")
            strings(reference["excluded"], path + ".excluded")
            if reference["status"] == "read":
                string(reference["use"], path + ".use")
            elif reference["status"] == "unavailable":
                if reference["use"] != "":
                    errors.append(path + ".use: unavailable references cannot supply claims")
            else:
                errors.append(path + ".status: expected read or unavailable")

    conflicts = document["conflicts"]
    if not isinstance(conflicts, list):
        errors.append("conflicts: expected list")
    else:
        for i, conflict in enumerate(conflicts):
            path = f"conflicts[{i}]"
            if obj(conflict, {"issue", "resolution"}, path):
                string(conflict["issue"], path + ".issue")
                if not isinstance(conflict["resolution"], str) or not conflict["resolution"].strip():
                    errors.append(path + ".resolution: unresolved conflict")

    tests = document["tests"]
    if not isinstance(tests, list) or not tests:
        errors.append("tests: expected nonempty list")
    else:
        for i, test in enumerate(tests):
            path = f"tests[{i}]"
            if obj(test, {"kind", "scenario", "expect"}, path):
                if test["kind"] not in ("normal", "edge", "stress"):
                    errors.append(path + ".kind: expected normal, edge or stress")
                string(test["scenario"], path + ".scenario")
                string(test["expect"], path + ".expect")
    return errors


def _fenced(text: str) -> str:
    runs = [len(match.group()) for match in re.finditer(r"`+", text)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return f"{fence}text\n{text}\n{fence}"


def _text(value: str) -> str:
    value = html.escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]#|!])", r"\\\1", value).replace("\n", " ")


def render(document: object) -> str:
    """Render an inspectable asset after structural validation."""
    errors = validate(document)
    if errors:
        raise ValueError("; ".join(errors))
    data = document
    prompt = ("任务目标：\n" + data["goal"].strip() + "\n\n" + data["template"].strip()
              + "\n\n约束要求：\n" + "\n".join("- " + item for item in data["constraints"])
              + "\n\n输出要求：\n" + "\n".join("- " + item for item in data["output_contract"]))
    # Only the template has slots. Other contract fields are literal text.
    filled_template = SLOT.sub(lambda match: data["variables"][match[1]]["example"], data["template"].strip())
    filled = ("任务目标：\n" + data["goal"].strip() + "\n\n" + filled_template
              + "\n\n约束要求：\n" + "\n".join("- " + item for item in data["constraints"])
              + "\n\n输出要求：\n" + "\n".join("- " + item for item in data["output_contract"]))
    lines = ["# " + _text(data["title"]), "", "## 可复用提示词", "", _fenced(prompt),
             "", "## 变量说明", ""]
    for name, spec in data["variables"].items():
        lines.append(f"- `{name}`: {_text(spec['description'])}")
    if not data["variables"]:
        lines.append("本模板无需填写变量。")
    lines += ["", "## 填写示例", "", "以下使用虚构输入演示填写方式，并非真实模型运行结果。", "", _fenced(filled),
              "", "## 来源取舍", ""]
    for reference in data["references"]:
        status_label = "已读取" if reference["status"] == "read" else "未能读取"
        lines += [f"- {_text(reference['id'])}（{status_label}）：{_text(reference['source'])}"]
        if reference["status"] == "read":
            lines.append("  采用的方法：" + _text(reference["use"]))
        else:
            lines.append("  未能读取，不据此采纳任何内容或结论。")
        for item in reference["excluded"]:
            lines.append("  不继承的内容：" + _text(item))
    if not data["references"]:
        lines.append("根据本次目标独立设计，未声称参考外部材料。")
    lines += ["", "## 冲突处理", ""]
    for conflict in data["conflicts"]:
        lines.append("- " + _text(conflict["issue"]) + " → " + _text(conflict["resolution"]))
    if not data["conflicts"]:
        lines.append("未记录冲突；这不代表脚本已自动验证内容不存在语义冲突。")
    lines += ["", "## 待执行的行为检查", "", "以下是测试清单，尚未针对目标模型执行。", ""]
    test_labels = {"normal": "正常输入", "edge": "边界情况", "stress": "压力情况"}
    for test in data["tests"]:
        lines.append(f"- **{test_labels[test['kind']]}** — {_text(test['scenario'])} 预期：{_text(test['expect'])}")
    return "\n".join(lines) + "\n"


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON: duplicate object key")
        result[key] = value
    return result


def _invalid_constant(_value: str) -> None:
    raise ValueError("JSON: nonstandard constant")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("output: must differ from input")
        if args.input.exists() and args.output.exists() and args.input.samefile(args.output):
            raise ValueError("output: must differ from input")
        with args.input.open(encoding="utf-8-sig") as stream:
            data = json.load(stream, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
        output = render(data)
        with args.output.open("w" if args.force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(output)
    except (OSError, ValueError, RecursionError) as error:
        if isinstance(error, json.JSONDecodeError):
            detail = f"JSON: invalid syntax at line {error.lineno}, column {error.colno}"
        elif isinstance(error, UnicodeError):
            detail = "input: expected UTF-8 text"
        elif isinstance(error, FileExistsError):
            detail = "output: exists; use --force only for an intended replacement"
        elif isinstance(error, OSError):
            detail = "file operation failed; check paths and permissions"
        elif isinstance(error, RecursionError):
            detail = "JSON: nesting too deep"
        else:
            detail = str(error)
        print("error: " + detail, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

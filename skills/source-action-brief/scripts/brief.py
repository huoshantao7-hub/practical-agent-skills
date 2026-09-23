#!/usr/bin/env python3
"""Offline source indexing and evidence-checked brief rendering. Python >= 3.10."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path


class BriefError(ValueError):
    """A user-correctable validation failure."""


def require(condition, message):
    if not condition:
        raise BriefError(message)


def fields(value, required, optional=(), label="object"):
    require(isinstance(value, dict), f"{label} must be an object")
    require(set(required) <= set(value), f"{label}: missing required fields")
    require(set(value) <= set(required) | set(optional), f"{label}: unknown fields")


def nonblank(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")
    return value


def sequence(value, label):
    require(isinstance(value, list), f"{label} must be an array")
    return value


def read_json(path):
    def unique_pairs(pairs):
        data = {}
        for key, value in pairs:
            require(key not in data, f"duplicate JSON key: {key}")
            data[key] = value
        return data
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BriefError(f"invalid UTF-8 JSON: {exc}") from exc


def build_index(source):
    source = Path(source)
    require(source.suffix.lower() in {".md", ".txt"}, "source must be a local UTF-8 .md or .txt file")
    raw = source.read_bytes()
    try:
        text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeError as exc:
        raise BriefError("source must be UTF-8; convert it explicitly first") from exc
    require("\x00" not in text, "source contains NUL; a binary file is not a text source")
    require(bool(text.strip()), "source is empty or whitespace-only")
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    paragraphs = []
    counts = {}
    start = None

    def add_paragraph(end):
        content = "\n".join(lines[start:end])
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        counts[digest] = counts.get(digest, 0) + 1
        paragraphs.append({
            "id": f"P-{digest}-{counts[digest]}",
            "start_line": start + 1,
            "end_line": end,
            "text": content,
        })

    for index, line in enumerate(lines):
        if line.strip():
            if start is None:
                start = index
        elif start is not None:
            add_paragraph(index)
            start = None
    if start is not None:
        add_paragraph(len(lines))
    return {
        "version": 1,
        "source_name": source.name,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "line_count": len(lines),
        "paragraphs": paragraphs,
    }


def markdown(value):
    """Display source strings as literal text, without active HTML or Markdown links."""
    value = html.escape(value, quote=False)
    return re.sub(r"([\\\x60*_{}\[\]()#+.!|>~-])", r"\\\1", value).replace("\n", " / ")


def validate_brief(index, brief):
    fields(brief, {"version", "source_sha256", "title", "evidence", "facts", "actions", "unknowns"}, label="brief")
    require(type(brief["version"]) is int and brief["version"] == 1, "unsupported brief version")
    require(brief["source_sha256"] == index["source_sha256"], "brief source hash differs; re-read current source")
    nonblank(brief["title"], "title")
    paragraphs = {paragraph["id"]: paragraph for paragraph in index["paragraphs"]}
    evidence = {}
    for number, item in enumerate(sequence(brief["evidence"], "evidence")):
        label = f"evidence[{number}]"
        fields(item, {"id", "paragraph_id", "start_line", "end_line", "quote"}, label=label)
        eid = item["id"]
        require(isinstance(eid, str) and re.fullmatch(r"E[1-9]\d*", eid) is not None, f"{label}: id must be E1, E2, ...")
        require(eid not in evidence, f"duplicate evidence id: {eid}")
        pid = item["paragraph_id"]
        require(isinstance(pid, str) and pid in paragraphs, f"{eid}: unknown paragraph_id")
        start, end = item["start_line"], item["end_line"]
        require(type(start) is int and type(end) is int, f"{eid}: line numbers must be integers")
        paragraph = paragraphs[pid]
        require(paragraph["start_line"] <= start <= end <= paragraph["end_line"], f"{eid}: line range lies outside paragraph")
        nonblank(item["quote"], f"{eid}.quote")
        local_start = start - paragraph["start_line"]
        local_end = end - paragraph["start_line"] + 1
        actual = "\n".join(paragraph["text"].split("\n")[local_start:local_end])
        require(item["quote"] == actual, f"{eid}: quote does not exactly match the complete selected source lines")
        evidence[eid] = item

    def refs(value, label, required=True):
        sequence(value, label)
        require(not required or len(value) > 0, f"{label} needs supporting evidence")
        result = []
        for eid in value:
            require(isinstance(eid, str) and eid in evidence, f"{label}: unknown evidence id")
            if eid not in result:
                result.append(eid)
        return result

    facts = []
    for number, fact in enumerate(sequence(brief["facts"], "facts")):
        fields(fact, {"text", "evidence"}, label=f"facts[{number}]")
        facts.append({"text": nonblank(fact["text"], "fact.text"), "evidence": refs(fact["evidence"], "fact.evidence")})

    def assignment(value, label):
        if value is None:
            return None
        fields(value, {"value", "evidence"}, label=label)
        text = nonblank(value["value"], f"{label}.value")
        ids = refs(value["evidence"], f"{label}.evidence")
        require(any(text in evidence[eid]["quote"] for eid in ids), f"{label}.value must occur verbatim in cited evidence")
        return {"value": text, "evidence": ids}

    actions = []
    for number, action in enumerate(sequence(brief["actions"], "actions")):
        fields(action, {"text", "basis", "owner", "due"}, label=f"actions[{number}]")
        actions.append({
            "text": nonblank(action["text"], "action.text"),
            "basis": refs(action["basis"], "action.basis"),
            "owner": assignment(action["owner"], "action.owner"),
            "due": assignment(action["due"], "action.due"),
        })
    unknowns = [nonblank(item, "unknown") for item in sequence(brief["unknowns"], "unknowns")]
    require(facts or actions or unknowns, "brief has no facts, actions, or unknowns")
    return {"title": brief["title"], "evidence": evidence, "facts": facts, "actions": actions, "unknowns": unknowns}


def render_report(index, checked):
    def refs(ids):
        return " ".join(f"[{eid}]" for eid in ids)

    def assignment(value):
        return "待确认（原文未明确）" if value is None else f'{markdown(value["value"])} {refs(value["evidence"])}'

    output = [
        f'# {markdown(checked["title"])}',
        "",
        f'来源：{markdown(index["source_name"])}',
        f'原文 SHA-256：\x60{index["source_sha256"]}\x60',
        "",
        "校验范围：原文版本、段落、行号、引文逐字匹配；事实是否被引文支持仍须人工或代理核读。",
        "",
        "## 事实摘要",
        "",
    ]
    output += [f'- {markdown(fact["text"])} {refs(fact["evidence"])}' for fact in checked["facts"]] or ["- 无可确认事实。"]
    output += ["", "## 建议行动（尚未执行）", ""]
    for number, action in enumerate(checked["actions"], 1):
        output += [
            f'{number}. {markdown(action["text"])}',
            f'   - 依据：{refs(action["basis"])}',
            f'   - 负责人：{assignment(action["owner"])}',
            f'   - 期限：{assignment(action["due"])}',
        ]
    if not checked["actions"]:
        output.append("- 无建议行动。")
    output += ["", "## 未知与待确认", ""]
    output += [f"- {markdown(item)}" for item in checked["unknowns"]] or ["- 本次未列出；不表示不存在。"]
    output += ["", "## 原文证据", ""]
    for eid, item in checked["evidence"].items():
        output += [
            f'### [{eid}] {item["paragraph_id"]} · L{item["start_line"]}–L{item["end_line"]}',
            "",
        ]
        output += ["> " + markdown(line) for line in item["quote"].split("\n")]
        output.append("")
    return "\n".join(output).rstrip() + "\n"


def write_new(path, text, inputs=()):
    target = Path(path)
    resolved = target.resolve()
    require(all(resolved != Path(item).resolve() for item in inputs), "output must not replace an input")
    require(not target.is_symlink(), "output must not be a symlink")
    require(target.parent.is_dir(), "output directory does not exist; create it explicitly first")
    try:
        with target.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except FileExistsError as exc:
        raise BriefError("output already exists; choose a new output path") from exc


def render(source, index_path, brief_path, out):
    index = read_json(index_path)
    current = build_index(source)
    require(index == current, "source or index changed; rebuild the index and review the brief")
    checked = validate_brief(current, read_json(brief_path))
    write_new(out, render_report(current, checked), (source, index_path, brief_path))
    return checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    index_cmd = commands.add_parser("index", help="index a local UTF-8 .md/.txt source")
    index_cmd.add_argument("source")
    index_cmd.add_argument("--out", required=True)
    render_cmd = commands.add_parser("render", help="validate an agent-written brief and render Markdown")
    render_cmd.add_argument("source")
    render_cmd.add_argument("--index", required=True)
    render_cmd.add_argument("--brief", required=True)
    render_cmd.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "index":
            result = build_index(args.source)
            write_new(args.out, json.dumps(result, ensure_ascii=False, indent=2) + "\n", (args.source,))
            print(f'OK: indexed {result["line_count"]} lines, {len(result["paragraphs"])} paragraphs')
        else:
            result = render(args.source, args.index, args.brief, args.out)
            print(f'OK: {len(result["facts"])} facts, {len(result["actions"])} actions; exact citations checked')
        return 0
    except (BriefError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# 数据合同 v1

所有 JSON 均为 UTF-8。每个对象只接受下列字段，未知字段、重复 JSON key、重复 evidence ID 都拒绝。Python 脚本不调用模型、不发网络请求、不执行资料中的命令。

## 索引

由 `index` 自动生成，不手改。

- `version`：1。
- `source_name`：文件名，不记录机器绝对路径。
- `source_sha256`：原始文件字节 SHA-256；换行/BOM 改动也会触发重审。
- `line_count`：行总数。CRLF/CR 在阅读与引文中统一成 LF；首个 UTF-8 BOM 去除。
- `paragraphs`：空行分段；每项含 `id`、`start_line`、`end_line`、`text`。
- 段落 ID 为 `P-<段落内容 SHA-256 前16位>-<同内容出现次数>`。插入其他内容不改变旧段落 ID；重复同文段落按出现顺序编号。行号从 1 开始，起止均含；一次引用不得跨段。

索引不是可信原文替身。`render` 重新读取 source 并构造索引，要求与已保存索引完全一致，检测原文变化或索引伪造。

## 简报 JSON

根对象全部必填：

| 字段 | 类型 | 用途 |
| --- | --- | --- |
| version | integer | 必须为 1 |
| source_sha256 | string | 从当前索引复制 |
| title | nonempty string | 报告标题 |
| evidence | array | 逐字证据 |
| facts | array | 仅原文明示事实 |
| actions | array | 尚未执行的建议 |
| unknowns | string array | 缺失信息、冲突、覆盖限制 |

facts/actions/unknowns 至少一项非空。证据结构：

    {"id":"E1","paragraph_id":"P-...-1","start_line":3,"end_line":4,"quote":"第三行全文\n第四行全文"}

ID 为 E1、E2 等不重复编号。quote 必须等于完整选中行，不支持省略号替换或只截取行内部分。引用应尽量短，可选择一个完整行；同一事实跨段时使用多个证据 ID。

事实结构：

    {"text":"原文明确表达的事实（保留限定语）","evidence":["E1"]}

建议结构：

    {"text":"建议采取的行动","basis":["E1"],"owner":null,"due":null}

owner/due 非空时是下列对象：

    {"value":"原文逐字的姓名或日期","evidence":["E2"]}

每条事实和建议必须有至少一个有效引用。重复使用同一引用 ID 会去重，不重复展示。owner/due 值必须逐字存在于其所引证据中，但**这不足以证明原文进行了任务分配**；代理还要核对原文是否把该行动分配给此人/时限，否则保持 null。禁止填“尽快”“今天”等无出处值。null 在报告显示为“待确认（原文未明确）”。

## 最小复现

在本技能目录运行：

    python scripts/brief.py index examples/source.md --out demo.index.json
    python scripts/brief.py render examples/source.md --index demo.index.json --brief examples/brief.json --out demo.report.md

示例内容是虚构测试资料。示例 brief 的哈希与仓库 source.md 的 LF 字节一致。跨平台检出不要改动该例换行；若曾改动，重新索引并核读后更新哈希或恢复原始文件。

成功返回 0，输入/引用/覆盖问题返回 2，错误写 stderr。验证失败不创建报告。输出目录须已存在，输出必须是新文件。

## 核验局限

脚本核对来源字节、段落 ID、合法行范围、精确引文与引用关系。它不证明事件真实性、摘要语义正确、建议必要性或负责人分配关系；这些必须由代理对照原文判断。本地执行的索引和校验不联网，但代理读取资料时仍遵循所在产品的数据处理方式。

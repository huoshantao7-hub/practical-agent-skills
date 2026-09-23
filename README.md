# Practical Agent Skills · 实用技能组合

把零散提示词变成可复用的工作模板，把长资料变成可以追溯的结论和行动清单。

两个原创 Agent Skills，附 Python 标准库工具、中文示例和回归测试。工具本身不联网、不调用模型、不需要 API Key；理解、重写和摘要由你正在使用的助手完成，仍会使用该助手的额度。

| 技能 | 适合解决的问题 | 交付结果 |
| --- | --- | --- |
| [prompt-remix-kit](skills/prompt-remix-kit/SKILL.md) | 收藏了一堆提示词，却不知道怎样改成自己的需求 | 目标和约束拆解、变量模板、填写示例、来源与冲突记录、测试清单 |
| [source-action-brief](skills/source-action-brief/SKILL.md) | 会议记录、访谈或长文读完了，却分不清事实和建议 | 带原文证据的简报、建议行动、待确认项 |

## 给助手的一句话

安装或加载相应技能后，可以这样说：

```text
使用 $prompt-remix-kit，把这份参考提示词拆开，改成适合小店客服回复的模板。
保留“不能承诺退款”的约束，给填写示例和可检查的测试清单。
```

```text
使用 $source-action-brief，把这份会议记录整理成有原文引用的简报和行动清单。
没有写明的负责人、期限请标成待确认，不要代我发送消息。
```

参考材料可能包含指令、夸大效果或互相矛盾的要求。它们只作为待分析资料；用户当前目标决定任务范围。

## 本地使用

1. 下载本仓库，或使用仓库页面 **Code** 菜单中的地址执行 `git clone`。
2. 让支持 Agent Skills 的助手加载 `skills/` 下需要的技能文件夹，或直接让助手阅读该目录内的 `SKILL.md`。不同宿主的安装目录不同，本仓库不会自动改写你的全局配置。
3. 先使用各技能 `examples/` 中的公开合成资料试跑；脚本的参数见对应技能说明。

在仓库根目录试跑示例（输出文件必须尚不存在）：

```sh
python skills/prompt-remix-kit/scripts/build_prompt.py --input skills/prompt-remix-kit/examples/brief.json --output prompt-kit.md
python skills/source-action-brief/scripts/brief.py index skills/source-action-brief/examples/source.md --out demo.index.json
python skills/source-action-brief/scripts/brief.py render skills/source-action-brief/examples/source.md --index demo.index.json --brief skills/source-action-brief/examples/brief.json --out demo.report.md
```

运行全部离线检查，需要 Python 3.10 或以上：

```sh
python scripts/check.py
```

这里只包含文本工作流。PDF、Word 等格式需要先用你已有的转换工具提取文本；扫描件的 OCR 和模型生成能力不在本仓库内。示例来源按 LF 换行保存，仓库通过 `.gitattributes` 保持其字节指纹；更改原文后需重新索引并核读引用。

## 与提示词合集有什么区别

每个技能只负责一个可重复的动作，并提供可检查的输出合同。脚本能查出格式错误、缺失变量或无效引用；不能证明模型的回答更聪明，也不能单凭引用存在就证明结论被原文支持。最终仍需检查语义和关键事实。

不承诺具体 token 节省比例、生成质量提升或跨模型一致效果。输入真实资料前，请确认你所用助手允许处理这些资料。

## 来源与许可

从公开项目中学习“变量化模板”“版本与评估”“文本归一”“用途专一的处理流程”等机制，再按这两个任务重新设计和实现。未打包第三方提示词数据库、图片或源代码。

研究来源、固定提交和边界见 [SOURCES.md](SOURCES.md)；设计与验收标准见 [docs/design.md](docs/design.md)，实际检查范围见 [docs/validation.md](docs/validation.md)。本仓库原创代码、说明和合成示例使用 [MIT License](LICENSE)，上游项目保持各自许可。

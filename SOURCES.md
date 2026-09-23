# 研究来源与原创实现边界

检查日期：2026-09-22。下表的 star 数来自检查时的 GitHub 官方接口快照，会持续变化；它们表示关注度，不代表效果或大众需求已经得到用户研究验证。选择理由还包括各项目公开文档中的常见使用场景。

| 官方项目与固定版本 | 关注度快照 | 拆出的机制 | 本仓库如何重组 | 上游许可 |
| --- | ---: | --- | --- | --- |
| [f/prompts.chat](https://github.com/f/prompts.chat/tree/f78a1c5136fa080155d928e0d7e2b4a41ddef03e) | 170,960 | 模板变量与填写值分离 | 显式变量合同、单次字面替换、独立模板和虚构示例 | 代码/站点内容 MIT；提示词数据 CC0，按该版本 LICENSE |
| [linshenkx/prompt-optimizer](https://github.com/linshenkx/prompt-optimizer/tree/897e56bf8af774c38b54cb2df0ebe5348ebac24c) | 35,417 | 提示词资产与评估、来源和示例的联系 | 来源取舍记录、显式冲突记录、未执行测试与实测分离 | AGPL-3.0-only；不复用其代码或提示词 |
| [microsoft/markitdown](https://github.com/microsoft/markitdown/tree/b8f79c57ebc0044be41323d89b2a45d3fda8460e) | 186,367 | 把多格式资料转为可处理文本 | 只接收离线文本，给原文行范围和指纹，转换器作为可选前置步骤 | MIT |
| [danielmiessler/Fabric](https://github.com/danielmiessler/Fabric/tree/95d0f957af463d64c0636b463da860ecd543370a) | 44,044 | 每个处理流程围绕一个明确用途组织输入和输出 | 原创“事实—证据—建议—待确认”报告合同 | MIT |

具体阅读的实现文件和逐项机制说明见两个技能各自的 `references/`。没有将上游实现作为依赖，也没有复制其提示词、源代码、示例或图片。根 LICENSE 只覆盖本仓库的原创实现，不改变上游许可，不表示获得上游作者背书。

最初参考的 [OpenNana 提示词图库](https://opennana.com/awesome-prompt-gallery) 同时展示免费和付费提示词。在本次检查中没有确认允许整库再分发的许可，因此未采集或打包其内容；它仅提供“发现后如何变成可复用资产”的问题背景。

## 原创增量

- 面向具体任务的两份中文技能，而不是搬运提示词集合。
- 不依赖供应商的 JSON 输入合同、Python 标准库校验器和 Markdown 导出。
- 把缺失信息、来源取舍、未解决冲突和未知事项保留在产物中。
- 默认不覆盖文件，合成用例可离线复现，引用校验的能力边界写进报告。

本仓库不声称这些基础概念由本项目首创；原创性在于为所述任务独立编写的组合、规则、代码和示例。对需求和成效的判断仍需实际用户反馈。

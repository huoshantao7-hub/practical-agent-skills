# 设计来源与原创边界

核验日期：2026-09-22。只借鉴可描述的机制，全部技能文本、数据合同、脚本和测试均为本项目原创；未复制上游提示词或代码，不需要安装任一上游项目。

| 上游 | 固定版本与核验文件 | 借鉴机制 | 本技能新增 |
| --- | --- | --- | --- |
| Microsoft MarkItDown | [README](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/README.md)、[核心转换器](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/packages/markitdown/src/markitdown/_markitdown.py) 的 convert_local 与 _convert | 将格式处理与后续文本分析分离；按输入选择转换器并归一文本 | 离线文本最小路径、原文指纹、稳定段落 ID、严格引文范围 |
| Daniel Miessler Fabric | [README](https://github.com/danielmiessler/Fabric/blob/95d0f957af463d64c0636b463da860ecd543370a/README.md)、[summarize pattern](https://github.com/danielmiessler/Fabric/blob/95d0f957af463d64c0636b463da860ecd543370a/data/patterns/summarize/system.md) | 按具体用途组织输入与输出约束 | 事实/建议/未知分离、证据图式、负责人和期限逐字出处、独立确定性校验 |

固定提交：

- MarkItDown：`b8f79c57ebc0044be41323d89b2a45d3fda8460e`，上游 [MIT 许可](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/LICENSE)。
- Fabric：`95d0f957af463d64c0636b463da860ecd543370a`，上游 [MIT 许可](https://github.com/danielmiessler/Fabric/blob/95d0f957af463d64c0636b463da860ecd543370a/LICENSE)。

上游源码只做阅读核验；不声称已安装或实测上游所有转换格式。本技能自带测试仅覆盖自身离线合同。MIT 许可并不代表关联、认可或背书。

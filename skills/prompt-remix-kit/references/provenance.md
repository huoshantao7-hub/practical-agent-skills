# Method provenance

This skill's prose, schema, Python implementation and fixtures are original. No upstream prompt collection, image, code, or user data is bundled. The root project license covers this original work; it does not relicense external sources.

Reviewed on 2026-09-22:

| Official repository / inspected revision | Evidence and useful mechanism | Upstream license |
| --- | --- | --- |
| [f/prompts.chat](https://github.com/f/prompts.chat/tree/f78a1c5136fa080155d928e0d7e2b4a41ddef03e) | API reported 170,960 stars at review; the [variable helper](https://github.com/f/prompts.chat/blob/f78a1c5136fa080155d928e0d7e2b4a41ddef03e/packages/prompts.chat/src/variables/index.ts) separates reusable placeholders from filled values. This skill instead uses a small explicit JSON contract and one unambiguous slot syntax. | [MIT for source/site content, CC0 for prompt data](https://github.com/f/prompts.chat/blob/f78a1c5136fa080155d928e0d7e2b4a41ddef03e/LICENSE). |
| [linshenkx/prompt-optimizer](https://github.com/linshenkx/prompt-optimizer/tree/897e56bf8af774c38b54cb2df0ebe5348ebac24c) | API reported 35,417 stars at review. Its [run-to-example mechanism](https://github.com/linshenkx/prompt-optimizer/blob/897e56bf8af774c38b54cb2df0ebe5348ebac24c/packages/core/src/services/prompt-model/example.ts) and [evaluation rewrite context](https://github.com/linshenkx/prompt-optimizer/blob/897e56bf8af774c38b54cb2df0ebe5348ebac24c/packages/core/src/services/evaluation/rewrite-from-evaluation.ts) distinguish reusable assets, sources and evaluation evidence. This skill borrows that product idea while keeping examples explicitly synthetic and proposed tests distinct from successful runs. | [AGPL-3.0-only](https://github.com/linshenkx/prompt-optimizer/blob/897e56bf8af774c38b54cb2df0ebe5348ebac24c/LICENSE); no code or prompt text reused. |

Stars indicate attention, not effectiveness or safety. The helper is not affiliated with either project. We deliberately omit the hosted catalog, accounts, provider settings, API calls and automatic quality claims. The useful output is a portable, inspectable prompt asset, not a cloned website.

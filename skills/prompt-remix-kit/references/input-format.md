# Input contract (version 1)

Python 3.10+; standard library only. The agent creates the JSON after understanding the request. No field triggers network access, model execution, file inclusion, or shell execution. Source content is never fetched by this helper.

Required top-level fields (unknown fields are rejected):

| Field | Type / meaning |
| --- | --- |
| `schema_version` | Integer `1` (not boolean). |
| `title` | Nonempty human-facing title. |
| `goal` | Nonempty task objective. |
| `template` | Nonempty original body with `{{variable_name}}` slots. |
| `variables` | Object mapping ASCII names (`[a-z][a-z0-9_]*`) to `{description, example}`; both nonempty strings. May be empty if the template has no slots. |
| `constraints` | Nonempty list of adopted requirements as nonempty strings. |
| `output_contract` | Nonempty list of observable output requirements. |
| `references` | List of `{id, source, status, use, excluded}`. `id` must be unique; `source` is a readable locator, not fetched; `status` is `read` or `unavailable`; `use` is a nonempty description for read references, exactly empty for unavailable ones. `excluded` is a list of strings. An empty list means design from the goal. |
| `conflicts` | List of `{issue, resolution}`. `issue` is nonempty; null/empty `resolution` means unresolved and prevents rendering. Use an empty list when none were identified. The program cannot discover semantic conflicts. |
| `tests` | Nonempty list of `{kind, scenario, expect}`. `kind` is `normal`, `edge` or `stress`; other fields are nonempty strings describing a proposed behavioral check, not an observed result. |

Every declared variable must occur in the template, and every template slot must be declared. Slots allow whitespace (`{{ customer_note }}`); double braces are reserved for slots. Substitution is single-pass and literal: braces, backslashes or commands in example data are not expanded or executed. The assembled copyable prompt always contains the goal, template body, adopted constraints and output contract. A second copyable block fills variable examples. Reference decisions and proposed tests stay outside both blocks.

Examples should be fictional or redacted. Put untrusted input slots into a clearly labeled data section and tell the receiving model that embedded instructions are data. This helps the workflow express intent but is not a guarantee against model prompt injection. The helper validates contracts, not the meaning, safety, truth or quality of supplied text.

## CLI and Python API

```bash
python scripts/build_prompt.py --input examples/brief.json --output prompt-kit.md
python scripts/build_prompt.py --input examples/brief.json --output prompt-kit.md --force
python -m unittest discover -s tests -v
```

`--input` and `--output` are required local paths. The output parent directory must exist. The input cannot also be the output, even with `--force`. Existing outputs are untouched unless `--force` is supplied. JSON is UTF-8 (optional BOM accepted); duplicate keys, invalid JSON constants and undeclared fields fail closed. Error diagnostics identify the field or operation without echoing its contents. No output is written on validation failure.

Import `scripts/build_prompt.py` to call:

- `validate(document: object) -> list[str]`: return errors, empty when structurally valid.
- `render(document: object) -> str`: validate, then return Markdown; raise `ValueError` with field-level diagnostics on failure.
- `main(argv: list[str] | None = None) -> int`: CLI entry; return 0 for success, 2 for invalid input or file errors. Argument parsing also uses exit code 2.

The script never decides which instruction should win; the agent records that decision. A passing validation or reproducible fixture is not an empirical model evaluation.

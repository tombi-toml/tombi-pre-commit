# tombi-pre-commit

A [pre-commit](https://pre-commit.com/) hook for [tombi](https://github.com/tombi-toml/tombi).

Distributed as a standalone repository to enable installing tombi via prebuilt wheels from
[PyPI](https://pypi.org/project/tombi/).

Mirrored tombi [`v1.5.5`](https://github.com/tombi-toml/tombi/releases/tag/v1.5.5) (commit: `b598e6fb9aab62cd5c8677ac832dd2a9c3b32e36`).

### Installation

To run `tombi format`, add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.5.5
  hooks:
    - id: tombi-format
```

To run `tombi lint`, add the following instead:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.5.5
  hooks:
    - id: tombi-lint
```

For both hooks, the `--offline` flag can be added to avoid network calls:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.5.5
  hooks:
    - id: tombi-format
      args: ["--offline"]
    - id: tombi-lint
      args: ["--offline"]
```

To use it with [prek](https://github.com/j178/prek), add this to your `prek.toml`:
```
[[repos]]
repo = "https://github.com/tombi-toml/tombi-pre-commit"
rev = "v1.4.1"
hooks = [
  { id = "tombi-format", args = ["--offline"] },
  { id = "tombi-lint", args = ["--offline"] },
]
```

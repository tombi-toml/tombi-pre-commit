# tombi-pre-commit

A [pre-commit](https://pre-commit.com/) hook for [tombi](https://github.com/tombi-toml/tombi).

Distributed as a standalone repository to enable installing tombi via prebuilt wheels from
[PyPI](https://pypi.org/project/tombi/).

### Installation

Add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v0.6.4
  hooks:
    - id: tombi-format
```

Optionally, you can also install the tombi linter as a pre-commit hook:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v0.6.4
  hooks:
    - id: tombi-format
    - id: tombi-lint
```

For both hooks, the `--offline` flag can be added to avoid network calls.
```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v0.6.4
  hooks:
    - id: tombi-format
      args: ["--offline"]
    - id: tombi-lint
      args: ["--offline"]
```

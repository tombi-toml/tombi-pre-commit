# tombi-pre-commit

A [pre-commit](https://pre-commit.com/) hook for [tombi](https://github.com/tombi-toml/tombi).

Distributed as a standalone repository to enable installing tombi via prebuilt wheels from
[PyPI](https://pypi.org/project/tombi/).

Mirrored tombi [`v1.2.2`](https://github.com/tombi-toml/tombi/releases/tag/v1.2.2) (commit: `b087cdd3d19b16f2673bc306ba7c265a178f00e0`).

### Installation

To run `tombi format`, add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.2.2
  hooks:
    - id: tombi-format
```

To run `tombi lint`, add the following instead:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.2.2
  hooks:
    - id: tombi-lint
```

For both hooks, the `--offline` flag can be added to avoid network calls:

```yaml
repos:
- repo: https://github.com/tombi-toml/tombi-pre-commit
  rev: v1.2.2
  hooks:
    - id: tombi-format
      args: ["--offline"]
    - id: tombi-lint
      args: ["--offline"]
```

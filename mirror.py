# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
#     "urllib3",
# ]
# ///
import re
import subprocess
from pathlib import Path

import tomllib
import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main():
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    # Get current version
    tombi_dep = Requirement(pyproject["project"]["dependencies"][0])
    current_version = Version(list(tombi_dep.specifier)[0].version)
    print(f"Current version: {current_version}")

    # Get newer versions from PyPI
    resp = urllib3.request("GET", "https://pypi.org/pypi/tombi/json")
    if resp.status != 200:
        raise RuntimeError

    versions = [Version(release) for release in resp.json()["releases"]]
    versions = sorted(
        v for v in versions if v > current_version and not v.is_prerelease
    )

    print(f"Versions to mirror: {versions}")
    for i, version in enumerate(versions):
        tag_name = f"v{version}"
        paths = update_version_in_files(version)

        subprocess.run(["git", "add", *paths], check=True)
        subprocess.run(["git", "commit", "-m", f"Tombi {tag_name}"], check=True)

        subprocess.run(["git", "tag", tag_name], check=True)
        subprocess.run(
            ["git", "push", "origin", "HEAD:refs/heads/main", "--tags"], check=True
        )

        gh_release_cmd = [
            "gh",
            "release",
            "create",
            tag_name,
            "--title",
            tag_name,
            "--notes",
            f"See: https://github.com/tombi-toml/tombi/releases/tag/{tag_name}",
            "--verify-tag",
        ]
        if i == len(versions) - 1:
            gh_release_cmd.append("--latest")
        subprocess.run(gh_release_cmd, check=True)


def update_version_in_files(version: Version) -> tuple[str, ...]:
    def replace_pyproject_toml(content: str) -> str:
        return re.sub(r'"tombi==.*"', f'"tombi=={version}"', content)

    def replace_readme_md(content: str) -> str:
        return re.sub(r"rev: v\d+\.\d+\.\d+", f"rev: v{version}", content)

    paths = {
        "pyproject.toml": replace_pyproject_toml,
        "README.md": replace_readme_md,
    }
    for path, replacer in paths.items():
        updated_content = replacer(content=Path(path).read_text())
        Path(path).write_text(updated_content)

    return tuple(paths.keys())


if __name__ == "__main__":
    main()

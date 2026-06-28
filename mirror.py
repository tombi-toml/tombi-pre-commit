# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
# ]
# ///
import argparse
import re
import subprocess
from pathlib import Path

from packaging.version import Version


TOMBI_REPOSITORY_URL = "https://github.com/tombi-toml/tombi.git"
TOMBI_COMMIT_URL_BASE = "https://github.com/tombi-toml/tombi/commit"
TOMBI_RELEASE_URL_BASE = "https://github.com/tombi-toml/tombi/releases/tag"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", help="Tombi version tag to mirror, for example v1.2.3")
    args = parser.parse_args()

    tag_name = args.version
    if not tag_name.startswith("v"):
        tag_name = f"v{tag_name}"

    version = Version(tag_name.removeprefix("v"))
    if version.is_prerelease:
        raise ValueError(f"Pre-release versions are not mirrored: {tag_name}")

    print(f"Version to mirror: {tag_name}")

    tag_exists = ref_exists(f"refs/tags/{tag_name}")
    has_release = release_exists(tag_name)
    if tag_exists and has_release:
        print(f"Tag and release {tag_name} already exist. Skipping release.")
        return

    if tag_exists:
        print(f"Tag {tag_name} already exists. Skipping commit and tag creation.")
    else:
        tombi_commit_sha = resolve_tombi_commit_sha(tag_name)
        print(f"Tombi commit to mirror: {tombi_commit_sha}")

        paths = update_version_in_files(version, tag_name, tombi_commit_sha)

        subprocess.run(["git", "add", *paths], check=True)
        if has_staged_changes():
            subprocess.run(["git", "commit", "-m", f"Tombi {tag_name}"], check=True)
        else:
            print("Version files are already up to date.")

        subprocess.run(["git", "tag", tag_name], check=True)
        subprocess.run(["git", "push", "origin", "HEAD:refs/heads/main"], check=True)
        subprocess.run(["git", "push", "origin", f"refs/tags/{tag_name}"], check=True)

    subprocess.run(
        [
            "gh",
            "release",
            "create",
            tag_name,
            "--title",
            tag_name,
            "--notes",
            f"See: https://github.com/tombi-toml/tombi/releases/tag/{tag_name}",
            "--verify-tag",
            "--latest=false",
        ],
        check=True,
    )


def ref_exists(ref: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "origin", ref],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 2:
        return False
    result.check_returncode()
    raise AssertionError("unreachable")


def release_exists(tag_name: str) -> bool:
    result = subprocess.run(
        ["gh", "release", "view", tag_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    result.check_returncode()
    raise AssertionError("unreachable")


def has_staged_changes() -> bool:
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        return False
    if result.returncode == 1:
        return True
    result.check_returncode()
    raise AssertionError("unreachable")


def resolve_tombi_commit_sha(tag_name: str) -> str:
    peeled_ref = f"refs/tags/{tag_name}^{{}}"
    result = subprocess.run(
        [
            "git",
            "ls-remote",
            TOMBI_REPOSITORY_URL,
            f"refs/tags/{tag_name}",
            peeled_ref,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    refs = {}
    for line in result.stdout.splitlines():
        sha, ref = line.split(maxsplit=1)
        refs[ref] = sha

    commit_sha = refs.get(peeled_ref) or refs.get(f"refs/tags/{tag_name}")
    if commit_sha is None:
        raise ValueError(f"Tombi tag does not exist: {tag_name}")
    if not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        raise ValueError(f"Unexpected tombi commit SHA for {tag_name}: {commit_sha}")

    return commit_sha


def update_version_in_files(
    version: Version, tag_name: str, tombi_commit_sha: str
) -> tuple[str, ...]:
    def replace_pyproject_toml(content: str) -> str:
        return re.sub(r'"tombi==.*"', f'"tombi=={version}"', content)

    def replace_readme_md(content: str) -> str:
        content = re.sub(r"rev: v\d+\.\d+\.\d+", f"rev: v{version}", content)
        tombi_commit_line = (
            "Mirrored tombi "
            f"[`{tag_name}`]({TOMBI_RELEASE_URL_BASE}/{tag_name}) commit: "
            f"[`{tombi_commit_sha}`]({TOMBI_COMMIT_URL_BASE}/{tombi_commit_sha})."
        )
        if "Mirrored tombi " in content:
            return re.sub(r"Mirrored tombi .+", tombi_commit_line, content)
        return content.replace(
            "[PyPI](https://pypi.org/project/tombi/).\n",
            f"[PyPI](https://pypi.org/project/tombi/).\n\n{tombi_commit_line}\n",
        )

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

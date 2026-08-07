# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
# ]
# ///
import subprocess
import unittest
from unittest.mock import patch

from packaging.version import Version

import mirror


class ResolveLatestTombiVersionTest(unittest.TestCase):
    @patch("mirror.subprocess.run")
    def test_returns_highest_stable_version(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="\n".join(
                [
                    "1" * 40 + "\trefs/tags/v1.2.7",
                    "2" * 40 + "\trefs/tags/v1.3.0-alpha.1",
                    "3" * 40 + "\trefs/tags/v1.2.8",
                    "4" * 40 + "\trefs/tags/v1.2.8^{}",
                ]
            ),
        )

        self.assertEqual(mirror.resolve_latest_tombi_version(), Version("1.2.8"))
        run.assert_called_once_with(
            [
                "git",
                "ls-remote",
                "--tags",
                mirror.TOMBI_REPOSITORY_URL,
                "refs/tags/v*",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("mirror.subprocess.run")
    def test_fails_when_no_stable_version_exists(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="1" * 40 + "\trefs/tags/v1.3.0-alpha.1",
        )

        with self.assertRaisesRegex(ValueError, "No stable Tombi tags found"):
            mirror.resolve_latest_tombi_version()


class ReleaseLatestOptionTest(unittest.TestCase):
    def test_marks_highest_stable_version_as_latest(self):
        self.assertEqual(
            mirror.release_latest_option(Version("1.2.8"), Version("1.2.8")),
            "--latest",
        )

    def test_does_not_mark_backfill_as_latest(self):
        self.assertEqual(
            mirror.release_latest_option(Version("1.2.7"), Version("1.2.8")),
            "--latest=false",
        )


class ExistingReleaseTest(unittest.TestCase):
    @patch("mirror.subprocess.run")
    @patch("mirror.release_exists", return_value=True)
    @patch("mirror.ref_exists", return_value=True)
    @patch("mirror.resolve_latest_tombi_version", return_value=Version("1.2.8"))
    @patch("sys.argv", ["mirror.py", "v1.2.8"])
    def test_marks_existing_highest_stable_release_as_latest(
        self, _resolve_latest, _ref_exists, _release_exists, run
    ):
        mirror.main()

        run.assert_called_once_with(
            ["gh", "release", "edit", "v1.2.8", "--latest"], check=True
        )

    @patch("mirror.subprocess.run")
    @patch("mirror.release_exists", return_value=True)
    @patch("mirror.ref_exists", return_value=True)
    @patch("mirror.resolve_latest_tombi_version", return_value=Version("1.2.8"))
    @patch("sys.argv", ["mirror.py", "v1.2.7"])
    def test_leaves_existing_backfill_release_unchanged(
        self, _resolve_latest, _ref_exists, _release_exists, run
    ):
        mirror.main()

        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

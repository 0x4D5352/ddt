import json
from pathlib import Path
from typing import Any
from ddt import models, constants
import argparse

"""
CLI Arg Parser
"""


def setup_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Tokenizer",
        description="Crawls a given directory, counts the number of tokens per filetype in the project and returns a per-type total and grand total",
        epilog="Made with <3 by 0x4D5352",
    )

    parser.add_argument(
        "directory",
        help="the relative or absolute path to the directory you wish to scan",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="set to increase logging to console",
    )

    parser.add_argument(
        "-g",
        "--include-gitignore",
        action="store_true",
        help="include files found in the .gitignore file, which are excluded by default",
    )
    parser.add_argument(
        "-d",
        "--include-dotfiles",
        action="store_true",
        help="include files and directories beginning with a dot (.), which are excluded by default - NOTE: not implemented yet.",
    )
    parser.add_argument(
        "-s",
        "--include-symlinks",
        action="store_true",
        help="include files and directories symlinked from outside the target directory, which are excluded by default.",
    )

    parser.add_argument(
        "-m",
        "--model",
        action="store",
        help="specify a model to use for token approximation. default is 'gpt-4o'",
        choices=constants.MODEL_CHOICES,
        default=constants.GPT_4O,
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store",
        help="save the results of the scan to a json file at the location specified. does not include stdout messages.",
    )

    file_types_group = parser.add_mutually_exclusive_group()
    file_types_group.add_argument(
        "-e",
        "--exclude",
        action="append",
        help="specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files",
    )
    file_types_group.add_argument(
        "-i",
        "--include",
        action="append",
        help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot be set if excluding files",
    )
    return parser


"""
Output methods
"""


class TokenEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, models.TokenCounter) or isinstance(o, models.FileCategory):
            return o.to_dict()
        return super().default(o)


def output_as_json(token_counter: models.TokenCounter, file_name: str) -> None:
    with open(file_name, "w") as file:
        json.dump(token_counter, file, cls=TokenEncoder, indent=2)


"""
Additional Helpers
"""


# TODO: implement https://github.com/cpburnz/python-pathspec for gitignore and rewrite from scratch
# AI wrote this code.
def parse_gitignore(root: Path) -> set[str]:
    """
    Reads the .gitignore file in the given root directory, interprets its patterns,
    and returns a set of Paths representing all files and directories within root that match
    those patterns. Lines that are empty or start with '#' (comments) are ignored.

    For pattern matching:
      - Patterns that start with '/' are treated as relative to the root.
      - Patterns that contain a slash (but do not start with '/') are also treated as relative.
      - Patterns without any slash are searched recursively using rglob.
      - If a pattern ends with '/', it is interpreted as a directory (the trailing slash is removed
        before matching).

    Args:
        root (Path): The root directory containing the .gitignore file.

    Returns:
        Set[Path]: A set of Paths that match the patterns specified in the .gitignore file.
    """
    ignored = set()
    gitignore_file = root / ".gitignore"

    try:
        with gitignore_file.open("r") as f:
            patterns = []
            for line in f:
                stripped = line.strip()
                # Skip empty lines or comments.
                if not stripped or stripped.startswith("#"):
                    continue
                patterns.append(stripped)
    except FileNotFoundError:
        return ignored  # No .gitignore file found.

    for pattern in patterns:
        # Check if the pattern is meant for directories (ends with a slash)
        if pattern.endswith("/"):
            # Remove trailing slash for glob matching.
            pattern = pattern.rstrip("/")

        # If the pattern starts with '/', it is anchored to the root.
        if pattern.startswith("/"):
            # Remove the leading slash.
            pattern = pattern[1:]
            # Use glob relative to the root (non-recursive).
            matches = root.glob(pattern)
        # If the pattern contains a slash somewhere, treat it as relative to the root.
        elif "/" in pattern:
            matches = root.glob(pattern)
        else:
            # Pattern without a slash: search recursively.
            matches = root.rglob(pattern)

        for match in matches:
            ignored.add(match)

    return ignored

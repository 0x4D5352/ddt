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
        help="include files and directories found in the .gitignore file",
    )
    parser.add_argument(
        "-d",
        "--include-dotfiles",
        action="store_true",
        help="include files and directories beginning with a dot (.)",
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
            return o._to_dict()
        return super().default(o)


def output_as_json(token_counter: models.TokenCounter, file_name: str) -> None:
    with open(file_name, "w") as file:
        json.dump(token_counter, file, cls=TokenEncoder, indent=2)


"""
Additional Helpers
"""

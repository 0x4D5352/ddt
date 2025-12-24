from pathlib import Path
import argparse
import sys
from . import tokenizer


# h/t to pedramamini: https://gist.github.com/pedramamini/ae9a881b13d89faf0a46d43f0b30bc7d
def read_stdin():
    try:
        return sys.stdin.buffer.read().decode("utf-8", errors="ignore")
    except AttributeError:
        return sys.stdin.read()


def read_file(path: Path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def setup_argparse() -> argparse.ArgumentParser:
    """
    Configures the CLI flags.
    """
    parser = argparse.ArgumentParser(
        prog="Tokenizer",
        description="Crawls a given directory, counts the number of tokens per filetype in the project and returns a per-type total and grand total",
        epilog="Made with <3 by 0x4D5352",
    )

    _ = parser.add_argument(
        "root",
        help="the relative or absolute path to the directory or file you wish to scan",
        type=Path,
    )

    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="set to increase logging to console",
    )

    _ = parser.add_argument(
        "-g",
        "--include-gitignore",
        action="store_true",
        help="include files and directories found in the .gitignore file",
    )
    _ = parser.add_argument(
        "-d",
        "--include-dotfiles",
        action="store_true",
        help="include files and directories beginning with a dot (.)",
    )
    _ = parser.add_argument(
        "-s",
        "--include-symlinks",
        action="store_true",
        help="include files and directories symlinked from outside the target directory",
    )
    _ = parser.add_argument(
        "-i",
        "--include-images",
        action="store_true",
        help="include image files found within the directory",
    )

    _ = parser.add_argument(
        "-r",
        "--resolve-paths",
        action="store_true",
        help="resolve relative file paths to their absolute location",
    )

    _ = parser.add_argument(
        "-m",
        "--model",
        action="store",
        help="specify a model to use for token approximation. default is 'gpt-4o'",
        choices=tokenizer.MODEL_CHOICES,
        default=tokenizer.GPT_4O,
        type=tokenizer.Model,
    )

    _ = parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="redirect output from STDOUT to a file at the location specified.",
        type=argparse.FileType(mode="w", encoding="UTF-8"),
        default=sys.stdout,
    )

    output_type_group = parser.add_mutually_exclusive_group()
    _ = output_type_group.add_argument(
        "--json",
        action="store_true",
        help="save the results of the scan to a json file",
        # deprecated=True,
    )
    _ = output_type_group.add_argument(
        "--html",
        action="store_true",
        help="save the results of the scan to a HTML file",
        deprecated=True,
    )

    input_filter_group = parser.add_mutually_exclusive_group()
    _ = input_filter_group.add_argument(
        "--exclude",
        action="append",
        help="specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files",
        type=str,
    )
    _ = input_filter_group.add_argument(
        "--include",
        action="append",
        help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot be set if excluding files",
        type=str,
    )
    return parser

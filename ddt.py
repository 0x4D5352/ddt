import argparse
import tiktoken
import json
from pathlib import Path
from math import ceil
from typing import Any
# import csv
# import yaml

GPT_4O = "gpt-4o"
GPT_4O_MINI = "gpt-4o-mini"
GPT_4_TURBO = "gpt-4-turbo"
GPT_4 = "gpt-4"

MODEL_CHOICES = [GPT_4O, GPT_4O_MINI, GPT_4_TURBO, GPT_4]


def main() -> None:
    print("Hello from tokenizer!")
    parser = setup_argparse()

    args = parser.parse_args()
    if len(args.directory) == 0:
        print("ERROR: No Directory Provided")
        exit(1)

    is_verbose = args.verbose

    if args.exclude is not None:
        excluded_filetypes: list[str] = args.exclude
    else:
        excluded_filetypes: list[str] = []

    if args.include is not None:
        included_filetypes: list[str] = args.include
    else:
        included_filetypes: list[str] = []

    root = Path(args.directory)
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        exit(1)

    print_with_separator("Parsing directory...", after=False)
    files = list(root.glob("**/*.*"))
    token_counter = TokenCounter(root, files)

    print("Parsing files...\n")
    for file in files:
        if file.is_dir():
            continue
        filename = file.name
        filetype = file.suffix[1:]
        if (filetype in excluded_filetypes or filetype not in included_filetypes) and (
            len(included_filetypes) > 0 or len(excluded_filetypes) > 0
        ):
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            # TODO: add to ignored_files
            continue
        print_if_verbose(f"reading {filename}", is_verbose)
        # TODO: implement mimetypes for choosing tokenization method: https://docs.python.org/3/library/mimetypes.html
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            # TODO: add to ignored_files
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            print(f"file {file.name} hit unicode error, ignoring from now on")
            continue
        token_counts = num_tokens_from_string(text, GPT_4O)
        if filetype not in token_counter.scanned_files:
            token_counter.scanned_files[filetype] = FileCategory(filetype)
        token_counter.scanned_files[filetype].files.append((filename, token_counts))
        token_counter.scanned_files[filetype].total += token_counts
        token_counter.total += token_counts

    print("\nParsing complete!")
    for extension, filetype in token_counter.scanned_files.items():
        print_with_separator(f"{extension} tokens:")
        for file in filetype.files:
            print(f"{file[0]}: {file[1]:,} tokens")
        print(f"{filetype.extension} total: {filetype.total:,} tokens")

    print_with_separator(f"grand total: {token_counter.total:,}")
    print(
        f"remaining tokens given 128K context window: {128_000 - token_counter.total:,}"
    )
    if args.output:
        output_as_json(token_counter, args.output)


"""
Data models
"""


class TokenCounter:
    """
    A class representing the contents of a directory and the count of tokens per file in that directory.

    Attributes:
        root(Path): The root path of the directory.
        all_files(list[Path]): All file paths in the directory.
        ignored_files(dict[str, list[Path]]): All files ignored by the scan, grouped by extension.
        scanned_files(dict[str, FileCategory]): All files scanned, grouped by extension.
        total(int): The total number of tokens present within the directory.
    """

    def __init__(self, root: Path, all_files: list[Path]) -> None:
        self.root: Path = root
        self.all_files: list[Path] = all_files
        self.ignored_files: dict[str, list[Path]] = {}
        self.scanned_files: dict[str, FileCategory] = {}
        self.total: int = 0

    def to_dict(self):
        return {
            "root": str(self.root),
            "all_files": [str(path) for path in self.all_files],
            "ignored_files": {
                key: [str(path) for path in paths]
                for key, paths in self.ignored_files.items()
            },
            "scanned_files": {
                ext: category.to_dict() for ext, category in self.scanned_files.items()
            },
            "total": self.total,
        }


class FileCategory:
    def __init__(self, extension: str) -> None:
        # TODO: decide if you even need this or if it's duplicate info from scanned_files dict
        self.extension: str = extension
        self.files: list[tuple[str, int]] = []
        self.total: int = 0

    def to_dict(self):
        return {
            "total": self.total,
            "files": [
                {"file": filename, "tokens": count} for filename, count in self.files
            ],
        }


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
        "-m",
        "--model",
        action="store",
        help="specify a model to use for token approximation. default is 'gpt-4o'",
        choices=MODEL_CHOICES,
        default=GPT_4O,
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="save the results of the scan to a file. does not include stdout messages.",
        # choices=["json", "csv", "yaml", "html"],
    )
    parser.add_argument(
        "--respect-gitignore",
        action="store_true",
        help="exclude files found in the .gitignore file",
    )
    parser.add_argument(
        "--ignore-dotfiles",
        action="store_true",
        help="exclude files and directories beginning with a dot (.)",
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
        help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot bet set if excluding files",
    )
    return parser


"""
Logging/Stdout Helpers
"""


def print_with_separator(string: str, after: bool = True) -> None:
    """
    A helper method to add line separators between sections of the stdout log.

    Args:
        string(string): the text to print.
        after(bool): If the text should print before or after the line separator. Defaults to after (True).
    """
    if not after:
        print(string)
    print("-------------------------------------------------")
    if after:
        print(string)


def print_if_verbose(string: str, is_verbose: bool) -> None:
    """
    A helper method that responds to the verbosity flag. is_verbose should always be set to the result of the is_verbose value in main()

    Args:
        string(string): the text to print.
        is_verbose(bool): If the text should print.
    """
    if not is_verbose:
        return
    print(string)


"""
Tokenizing methods
"""


def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string"""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Source for image token code: https://medium.com/@teekaifeng/gpt4o-visual-tokenizer-an-illustration-c69695dd4a39
"""
Adapted from https://community.openai.com/t/how-do-i-calculate-image-tokens-in-gpt4-vision/492318/2 
"""


def calculate_image_tokens(width: int, height: int) -> int:
    # Step 1: scale to fit within a 2048 x 2048 square (maintain aspect ratio)
    if width > 2048 or height > 2048:
        aspect_ratio = width / height
        if aspect_ratio > 1:
            width, height = 2048, int(2048 / aspect_ratio)
        else:
            width, height = int(2048 * aspect_ratio), 2048

    # Step 2: scale such that the shortest side of the image is 768px long
    if width >= height and height > 768:
        width, height = int((768 / height) * width), 768
    elif height > width and width > 768:
        width, height = 768, int((768 / width) * height)

    # Step 3: compute number of 512x512 tiles that can fit into the image
    tiles_width = ceil(width / 512)
    tiles_height = ceil(height / 512)

    # See https://platform.openai.com/docs/guides/vision/calculating-costs
    #   - 85 is the "base token" that will always be added
    #   - 1 tiles = 170 tokens
    total_tokens = 85 + 170 * (tiles_width * tiles_height)

    return total_tokens


"""
Output methods
"""


class TokenEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, TokenCounter) or isinstance(o, FileCategory):
            return o.to_dict()
        return super().default(o)


def output_as_json(token_counter: TokenCounter, file_name: str) -> None:
    with open(file_name, "w") as file:
        # TODO: make tokencounter serializable: https://docs.python.org/3/library/json.html#encoders-and-decoders
        json.dump(token_counter, file, cls=TokenEncoder, indent=2)


if __name__ == "__main__":
    main()

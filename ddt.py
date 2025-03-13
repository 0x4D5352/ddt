import argparse
import tiktoken
from pathlib import Path
from math import ceil
import json
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
    token_counter = TokenCounter(files)

    print("Parsing files...\n")
    for file in files:
        if "old" in file.__str__() and args.exclude_old:
            print(f"file {file.name} marked as old, skipping for now")
            continue
        if file.is_dir():
            continue
        filename = file.name
        filetype = file.suffix[1:]
        if (filetype in excluded_filetypes or filetype not in included_filetypes) and (
            len(included_filetypes) > 0 or len(excluded_filetypes) > 0
        ):
            continue
        print_if_verbose(f"reading {filename}", is_verbose)
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            excluded_filetypes.append(filetype)
            print(f"file {file.name} hit unicode error, ignoring from now on")
            continue
        token_counts = num_tokens_from_string(text, GPT_4O)
        if filetype not in token_counter.file_categories:
            token_counter.file_categories[filetype] = FileCategory(filetype)
        token_counter.file_categories[filetype].files.append((filename, token_counts))
        token_counter.file_categories[filetype].total += token_counts
        token_counter.total += token_counts

    print("\nParsing complete!")
    for extension, filetype in token_counter.file_categories.items():
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
    def __init__(self, file_paths: list[Path]) -> None:
        self.file_paths: list[Path] = file_paths
        self.file_categories: dict[str, FileCategory] = {}
        self.total: int = 0


class FileCategory:
    def __init__(self, extension: str) -> None:
        self.extension: str = extension
        self.files: list[tuple[str, int]] = []
        self.total: int = 0


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
        "--exclude_old",
        action="store_true",
        help="ignore directories and files with 'old' in the name.",
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


def output_as_json(token_counter: TokenCounter, file_name: str) -> None:
    with open(file_name, "w") as file:
        # TODO: make tokencounter serializable
        json.dump(token_counter, file)


if __name__ == "__main__":
    main()

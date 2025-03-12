import argparse
import tiktoken
from pathlib import Path

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

    print("Parsing directory...")
    print_separator()
    files = list(root.glob("**/*.*"))
    file_categories: dict[str, list[tuple[str, int]]] = {}
    category_totals: dict[str, int] = {}
    running_total = 0

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
        if filetype not in file_categories:
            file_categories[filetype] = []
            category_totals[filetype] = 0
        file_categories[filetype].append((filename, token_counts))
        category_totals[filetype] += token_counts
        running_total += token_counts

    print("\nParsing complete!")
    for filetype, count in category_totals.items():
        print_separator()
        print(f"{filetype} tokens:")
        for file in file_categories[filetype]:
            print(f"{file[0]}: {file[1]:,} tokens")
        print(f"{filetype} total: {count:,} tokens")

    print_separator()
    print(f"grand total: {running_total:,}")
    print(f"remaining tokens given 128K context window: {128_000 - running_total:,}")


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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--exclude",
        action="append",
        help="specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files",
    )
    group.add_argument(
        "-i",
        "--include",
        action="append",
        help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot bet set if excluding files",
    )
    parser.add_argument(
        "-m--model",
        action="store",
        help="specify a model to use for token approximation. default is 'gpt-4o'",
        choices=MODEL_CHOICES,
        default=GPT_4O,
    )
    return parser


def print_separator() -> None:
    print("-------------------------------------------------")


def print_if_verbose(string: str, is_verbose: bool) -> None:
    if not is_verbose:
        return
    print(string)


def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string"""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == "__main__":
    main()

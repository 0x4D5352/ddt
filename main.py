import mimetypes
from sys import exit as sysexit
from ddt import cli, logging, tokenizer, models
from pathlib import Path

"""
Main function
"""


def main() -> None:
    print("Hello from tokenizer!")
    parser = cli.setup_argparse()

    # NOTE: maybe i just want to pass this to the tokencounter?
    args = parser.parse_args()
    if len(args.directory) == 0:
        print("ERROR: No Directory Provided")
        sysexit(1)

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        sysexit(1)

    token_counter = models.TokenCounter(root)
    token_counter.add_exclusions(args.exclude)
    token_counter.add_inclusions(args.include)

    mimetypes.init()
    print("Parsing files...\n")
    # TODO: make a class method
    for file in token_counter.all_files:
        if file.is_dir():
            continue
        filename = file.name
        filetype = grab_suffix(file)
        mime_grabber = mimetypes.guess_file_type(file)
        print(f"mime: {mime_grabber}")
        # mime_map = mimetypes.types_map[f".{filetype}"]
        # print(f"mime from map: {mime_map}")

        def add_to_ignored(file: Path, filetype: str):
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)

        if (
            len(token_counter.included_files) > 0
            and file not in token_counter.included_files
        ):
            add_to_ignored(file, filetype)
            continue

        if (
            len(token_counter.excluded_files) > 0
            and file in token_counter.excluded_files
        ):
            add_to_ignored(file, filetype)
            continue

        if not args.include_dotfiles and any(
            part.startswith(".") for part in file.parts
        ):
            add_to_ignored(file, filetype)
            continue

        if not args.include_gitignore and file in token_counter.gitignore:
            add_to_ignored(file, filetype)
            continue

        if not args.include_symlinks and root.name not in file.parts:
            add_to_ignored(file, filetype)
            continue

        logging.print_if_verbose(f"reading {str(file)}", args.verbose)
        # TODO: implement mimetypes for choosing tokenization method: https://docs.python.org/3/library/mimetypes.html
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            print(f"file {file.name} hit unicode error, ignoring")
            continue
        token_counts = tokenizer.num_tokens_from_string(text, args.model)
        if filetype not in token_counter.scanned_files:
            token_counter.scanned_files[filetype] = models.FileCategory(filetype)
        token_counter.scanned_files[filetype].files.append(
            {"file": filename, "tokens": token_counts}
        )
        token_counter.scanned_files[filetype].total += token_counts
        token_counter.total += token_counts

    print("\nParsing complete!")
    if args.verbose:
        for extension, ignored in token_counter.ignored_files.items():
            logging.print_with_separator(f"{extension} files ignored:")
            for file in ignored:
                print(str(file))

    for extension, filetype in token_counter.scanned_files.items():
        logging.print_with_separator(f"{extension} tokens:")
        for file in filetype.files:
            print(f"{file['file']}: {file['tokens']:,} tokens")
        print(f"{filetype.extension} total: {filetype.total:,} tokens")

    logging.print_with_separator(f"grand total: {token_counter.total:,}")
    print(
        f"remaining tokens given 128K context window: {128_000 - token_counter.total:,}"
    )
    if args.json:
        cli.output_as_json(token_counter, args.json)


def grab_suffix(file: Path) -> str:
    if len(file.suffixes) == 1:
        return file.suffix[1:]
    result = ""
    for index, suffix in enumerate(file.suffixes):
        if index == 0:
            result += suffix[1:]
        else:
            result += suffix
    return result


if __name__ == "__main__":
    main()

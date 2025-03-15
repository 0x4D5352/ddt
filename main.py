from ddt import cli, logging, tokenizer, models
from pathlib import Path

"""
Main function
"""


def main() -> None:
    print("Hello from tokenizer!")
    parser = cli.setup_argparse()

    args = parser.parse_args()
    if len(args.directory) == 0:
        print("ERROR: No Directory Provided")
        exit(1)

    is_verbose = args.verbose

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        exit(1)

    if args.exclude is not None:
        excluded_files: list[Path] = [
            file.resolve() for file in root.glob(f"**/*.{args.exclude}")
        ]
    else:
        excluded_files: list[Path] = []

    if args.include is not None:
        included_files: list[Path] = [
            file.resolve() for file in root.glob(f"**/*.{args.include}")
        ]
    else:
        included_files: list[Path] = []

    if args.respect_gitignore:
        gitignore = cli.parse_gitignore(root)
    else:
        gitignore = None

    logging.print_with_separator("Parsing directory...", after=False)
    files = [file.resolve() for file in root.glob("**/*.*")]
    token_counter = models.TokenCounter(root, files)

    print("Parsing files...\n")
    for file in files:
        if file.is_dir():
            continue
        filename = file.name
        filetype = file.suffix[1:]
        if (
            (
                (file in excluded_files or file not in included_files)
                and (len(included_files) > 0 or len(excluded_files) > 0)
            )
            or (file.name[0] == "." and args.ignore_dotfiles)
            or (gitignore is not None and file in gitignore)
        ):
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            continue
        logging.print_if_verbose(f"reading {filename}", is_verbose)
        # TODO: implement mimetypes for choosing tokenization method: https://docs.python.org/3/library/mimetypes.html
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            print(f"file {file.name} hit unicode error, ignoring from now on")
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


if __name__ == "__main__":
    main()

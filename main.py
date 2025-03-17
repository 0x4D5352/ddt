from sys import exit as sysexit
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
        sysexit(1)

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        sysexit(1)

    if args.exclude is not None:
        excluded_files: list[Path] = []
        for ext in args.exclude:
            excluded_files.extend(file.resolve() for file in root.glob(f"**/*.{ext}"))
    else:
        excluded_files: list[Path] = []

    if args.include is not None:
        included_files: list[Path] = []
        for ext in args.include:
            included_files.extend(file.resolve() for file in root.glob(f"**/*.{ext}"))
    else:
        included_files: list[Path] = []

    if not args.include_gitignore:
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
        filetype = grab_suffix(file)

        # TODO: decide if four precomp'd conditions and one big if is better or if four independent if checks are better.
        is_excluded = len(excluded_files) > 0 and file in excluded_files
        is_not_included = len(included_files) > 0 and file not in included_files
        is_dotfile = not args.include_dotfiles and any(
            part.startswith(".") for part in file.parts
        )
        is_gitignored = gitignore is not None and file in gitignore
        is_symlink = args.include_symlinks

        if is_excluded or is_not_included or is_dotfile or is_gitignored:
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)
            continue

        logging.print_if_verbose(f"reading {str(file)}", args.verbose)
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

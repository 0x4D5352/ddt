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

    token_counter = models.TokenCounter(root, args.model)
    token_counter.add_exclusions(args.exclude)
    token_counter.add_inclusions(args.include)

    mimetypes.init()
    print("Parsing files...\n")
    # TODO: make a class method
    for file in token_counter.all_files:
        logging.print_if_verbose(f"checking {str(file)}", args.verbose)
        if file.is_dir():
            continue
        file_extension = grab_suffix(file)
        mime: str | None = (
            mimetypes.types_map[file_extension]
            if file_extension in mimetypes.types_map
            else None
        )
        print(f"mime from map: {mime}")

        def add_to_ignored(file: Path, filetype: str):
            if filetype not in token_counter.ignored_files:
                token_counter.ignored_files[filetype] = []
            token_counter.ignored_files[filetype].append(file)

        if (
            len(token_counter.included_files) > 0
            and file not in token_counter.included_files
        ):
            add_to_ignored(file, file_extension)
            continue

        if (
            len(token_counter.excluded_files) > 0
            and file in token_counter.excluded_files
        ):
            add_to_ignored(file, file_extension)
            continue

        if not args.include_dotfiles and any(
            part.startswith(".") for part in file.parts
        ):
            add_to_ignored(file, file_extension)
            continue

        if not args.include_gitignore and file in token_counter.gitignore:
            add_to_ignored(file, file_extension)
            continue

        if not args.include_symlinks and root.name not in file.parts:
            add_to_ignored(file, file_extension)
            continue

        logging.print_if_verbose(f"reading {str(file)}", args.verbose)

        if mime:
            category = mime.split("/")[0]
            match category:
                case "text" | "json":
                    token_counts = token_counter.count_text_file(file, file_extension)
                case "image":
                    # TODO: figure out how to let the user decide on if they're including images or not. maybe default to not?
                    token_counts = token_counter.count_image_file(file, file_extension)
                case _:
                    # TODO: have a better way of doing this
                    token_counts = token_counter.count_text_file(file, file_extension)
        else:
            # TODO: fix this logic
            token_counts = 0
        if file_extension not in token_counter.scanned_files:
            token_counter.scanned_files[file_extension] = models.FileCategory(
                file_extension
            )
        token_counter.scanned_files[file_extension].files.append(
            {"file": file.name, "tokens": token_counts}
        )
        token_counter.scanned_files[file_extension].total += token_counts
        token_counter.total += token_counts

    print("\nParsing complete!")
    if args.verbose:
        for extension, ignored in token_counter.ignored_files.items():
            logging.print_with_separator(f"{extension} files ignored:")
            for file in ignored:
                print(str(file))

    for extension, file_extension in token_counter.scanned_files.items():
        logging.print_with_separator(f"{extension} tokens:")
        for file in file_extension.files:
            print(f"{file['file']}: {file['tokens']:,} tokens")
        print(f"{file_extension.extension} total: {file_extension.total:,} tokens")

    logging.print_with_separator(f"grand total: {token_counter.total:,}")
    print(
        f"remaining tokens given 128K context window: {128_000 - token_counter.total:,}"
    )
    if args.json:
        cli.output_as_json(token_counter, args.json)


def grab_suffix(file: Path) -> str:
    if len(file.suffixes) == 1:
        return file.suffix
    result = ""
    for suffix in file.suffixes:
        result += suffix
    return result


if __name__ == "__main__":
    main()

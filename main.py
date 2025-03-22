from sys import exit as sysexit
from ddt import io, logging, models

"""
Main function
"""


def main() -> None:
    print("Hello from tokenizer!")

    # TODO: create an API-able endpoint or the ability to feed a JSON blob for parsing
    scanner = io.CLI()

    if not scanner.directory_path:
        print("ERROR: No Directory Provided")
        sysexit(1)

    root = scanner.directory_path.resolve()
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        sysexit(1)

    token_counter = models.TokenCounter(root, scanner.model)
    token_counter.add_exclusions(scanner.exclude)
    token_counter.add_inclusions(scanner.include)

    print("Parsing files...\n")
    # TODO: make a class method

    print("\nParsing complete!")
    logging.print_with_separator("ignored:", sep="=")
    if scanner.is_verbose:
        for extension, ignored in token_counter.ignored_files.items():
            logging.print_with_separator(f"{extension} files ignored:", sep="*")
            for file in ignored:
                print(str(file))

    logging.print_with_separator("totals:")
    for extension, file_extension in token_counter.scanned_files.items():
        logging.print_with_separator(f"{extension} tokens:", sep="*")
        for file in file_extension.files:
            print(f"{file['file']}: {file['tokens']:,} tokens")
        logging.print_with_separator(
            f"{file_extension.extension} total: {file_extension.total:,} tokens",
            ".",
        )

    logging.print_with_separator(f"grand total: {token_counter.total:,}")
    print(
        f"remaining tokens given 128K context window: {128_000 - token_counter.total:,}"
    )
    if scanner.json_destination:
        io.output_as_json(token_counter, scanner.json_destination)


if __name__ == "__main__":
    main()

from sys import exit as sysexit
from ddt import cli, logging, models

"""
Main function
"""


def main() -> None:
    config = cli.CLI().generate_config()
    logging.print_if_verbose("Hello from tokenizer!", config.is_verbose)

    if not config.root:
        print("ERROR: No Directory Provided")
        sysexit(1)

    root = config.root.resolve()
    if not root.is_dir():
        print("ERROR: Path Provided Is Not A Directory")
        sysexit(1)

    token_counter = models.TokenCounter(config)
    token_counter.add_exclusions(config.exclude)
    token_counter.add_inclusions(config.include)

    logging.print_if_verbose("Parsing files...", token_counter.config.is_verbose)

    token_counter.parse_files()

    logging.print_if_verbose("Parsing complete!", token_counter.config.is_verbose)
    if config.is_verbose:
        logging.print_with_separator("ignored:", sep="=")
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
    if config.json_destination:
        token_counter.output_as_json()


if __name__ == "__main__":
    main()

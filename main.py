from sys import exit as sysexit
from src import cli, logging, models

"""
Main function
"""


def main() -> None:
    config = cli.CLI().generate_config()

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

    # TODO: convert this to just output
    if config.output:
        token_counter.output()


if __name__ == "__main__":
    main()

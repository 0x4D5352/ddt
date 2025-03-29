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

    token_counter.output()


if __name__ == "__main__":
    main()

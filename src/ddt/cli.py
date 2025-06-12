import logging
from src import parser, models

"""
Main function
"""


def main() -> None:
    config = parser.CLIParser().generate_config()

    token_counter = models.TokenCounter(config)
    token_counter.add_exclusions(config.exclude)
    token_counter.add_inclusions(config.include)

    logging.debug("Parsing files...")

    token_counter.parse_files()

    logging.debug("Parsing complete!")

    token_counter.output()


if __name__ == "__main__":
    main()

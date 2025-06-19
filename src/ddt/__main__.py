import logging
from . import cli, models

"""
Main function
"""


def main() -> None:
    p = cli.setup_argparse()
    args = p.parse_args()
    config = cli.generate_config(args)

    token_counter = models.TokenCounter(config)
    token_counter.add_exclusions(config.exclude)
    token_counter.add_inclusions(config.include)

    logging.debug("Parsing files...")

    token_counter.parse_files()

    logging.debug("Parsing complete!")

    token_counter.output()


if __name__ == "__main__":
    main()

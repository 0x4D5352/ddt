import logging
from . import cli, config, models

"""
Main function
"""


def main() -> None:
    p = cli.setup_argparse()
    args = p.parse_args()
    cfg = config.generate_config(args)

    token_counter = models.TokenCounter(cfg)
    token_counter.add_exclusions(cfg.exclude)
    token_counter.add_inclusions(cfg.include)

    logging.debug("Parsing files...")

    token_counter.parse_files()

    logging.debug("Parsing complete!")

    token_counter.output()


if __name__ == "__main__":
    main()

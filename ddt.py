from src import cli, models

"""
Main function
"""


def main() -> None:
    config = cli.Parser().generate_config()

    token_counter = models.TokenCounter(config)
    token_counter.add_exclusions(config.exclude)
    token_counter.add_inclusions(config.include)


    token_counter.parse_files()


    token_counter.output()


if __name__ == "__main__":
    main()

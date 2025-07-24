import logging
import sys
from pathlib import Path
from . import cli, config, models, tokenizer

"""
Main function
"""


# h/t to pedramamini: https://gist.github.com/pedramamini/ae9a881b13d89faf0a46d43f0b30bc7d
def read_stdin():
    try:
        return sys.stdin.buffer.read().decode("utf-8", errors="ignore")
    except AttributeError:
        return sys.stdin.read()


def read_file(path: Path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main() -> None:
    if len(sys.argv) == 0:
        standard_input = read_stdin()
        print(
            tokenizer.calculate_text_tokens(standard_input, tokenizer.GPT_4O),
            file=sys.stdout,
        )
        sys.exit(0)
    p = cli.setup_argparse()
    args = p.parse_args()
    target: Path = args.target
    if not target.exists():
        print(f"File '{target.name}' not found.", file=sys.stderr)
        sys.exit(1)
    if target.is_file():
        file = read_file(target)
        model = args.model
        print(tokenizer.calculate_text_tokens(file, model))

    cfg = config.generate_config(vars(args))

    token_counter = models.TokenCounter(cfg)
    token_counter.add_exclusions(cfg.exclude)
    token_counter.add_inclusions(cfg.include)

    logging.debug("Parsing files...")

    token_counter.parse_files()

    logging.debug("Parsing complete!")

    token_counter.output()


if __name__ == "__main__":
    main()

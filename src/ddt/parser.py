from pathlib import Path
from sys import exit as sysexit
import json
import argparse
import sys
import logging
from typing import final
from . import models


"""
CLI Arg Parser
"""


@final
class CLIParser:
    def __init__(self) -> None:
        self.parser = self.setup_argparse()
        self.args: argparse.Namespace | None = None

    def parse_args(self, argv: list[str] | None = None) -> None:
        self.args = self.parser.parse_args(argv)
        self._setup_logging()

    # TODO: set this up in the config instead
    def _setup_logging(self) -> None:
        level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(format='%(message)s', level=level)

    def setup_argparse(self) -> argparse.ArgumentParser:
        """
        Configures the CLI flags.
        """
        parser = argparse.ArgumentParser(
            prog="Tokenizer",
            description="Crawls a given directory, counts the number of tokens per filetype in the project and returns a per-type total and grand total",
            epilog="Made with <3 by 0x4D5352",
        )

        parser.add_argument(
            "directory",
            help="the relative or absolute path to the directory you wish to scan",
            type=Path,
        )

        parser.add_argument(
            "-c",
            "--config",
            action="store",
            help="Load one or more configurations from a file. Unset configs will use defaults.",
            type=argparse.FileType(mode="r", encoding="UTF-8"),
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="set to increase logging to console",
        )

        parser.add_argument(
            "-g",
            "--include-gitignore",
            action="store_true",
            help="include files and directories found in the .gitignore file",
        )
        parser.add_argument(
            "-d",
            "--include-dotfiles",
            action="store_true",
            help="include files and directories beginning with a dot (.)",
        )
        parser.add_argument(
            "-s",
            "--include-symlinks",
            action="store_true",
            help="include files and directories symlinked from outside the target directory",
        )
        parser.add_argument(
            "-i",
            "--include-images",
            action="store_true",
            help="include image files found within the directory",
        )

        parser.add_argument(
            "-r",
            "--resolve-paths",
            action="store_true",
            help="resolve relative file paths to their absolute location",
        )

        parser.add_argument(
            "-m",
            "--model",
            action="store",
            help="specify a model to use for token approximation. default is 'gpt-4o'",
            choices=models.MODEL_CHOICES,
            default=models.GPT_4O,
            type=models.Model,
        )

        parser.add_argument(
            "-o",
            "--output",
            action="store",
            help="redirect output from STDOUT to a file at the location specified.",
            type=argparse.FileType(mode="w", encoding="UTF-8"),
            default=sys.stdout,
        )

        output_type_group = parser.add_mutually_exclusive_group()
        output_type_group.add_argument(
            "--json",
            action="store_true",
            help="save the results of the scan to a json file",
        )
        output_type_group.add_argument(
            "--html",
            action="store_true",
            help="save the results of the scan to a HTML file",
        )

        input_filter_group = parser.add_mutually_exclusive_group()
        input_filter_group.add_argument(
            "--exclude",
            action="append",
            help="specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files",
            type=str,
        )
        input_filter_group.add_argument(
            "--include",
            action="append",
            help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot be set if excluding files",
            type=str,
        )
        return parser

    def generate_config(self) -> models.Config:
        """
        Basically the main function of this class - it converts the CLI config into a system config
        """
        if self.args.config:
            with self.args.config.open("r") as json_conf:
                conf = json.load(json_conf)
        else:
            conf = dict()

        if self.args.json:
            output_format = "json"
        elif self.args.html:
            output_format = "html"
        else:
            output_format = "txt"
        for arg, value in vars(self.args).items():
            if arg == "config" or arg in conf.keys():
                continue
            conf[arg] = value

        if conf["exclude"] and conf["include"]:
            print(
                "error: both inclusions and exclusions found. please remove one group"
            )
            sysexit(1)

        root = conf["directory"].resolve()
        if not root.is_dir():
            print("ERROR: Path Provided Is Not A Directory")
            sysexit(1)

        cfg = models.Config(
            root=root,
            is_verbose=conf["verbose"],
            include_gitignore=conf["include_gitignore"],
            include_dotfiles=conf["include_dotfiles"],
            include_symlinks=conf["include_symlinks"],
            include_images=conf["include_images"],
            resolve_paths=conf["resolve_paths"],
            model=conf["model"],
            output=conf["output"],
            output_format=output_format,
            exclude=conf["exclude"],
            include=conf["include"],
        )
        return cfg

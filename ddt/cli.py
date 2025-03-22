from pathlib import Path
import json
import argparse
from . import models


"""
CLI Arg Parser
"""


class CLI:
    def __init__(self) -> None:
        parser = self.setup_argparse()
        self.args = parser.parse_args()

    def setup_argparse(self) -> argparse.ArgumentParser:
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
            "-j",
            "--json",
            action="store",
            help="save the results of the scan to a json file at the location specified. does not include stdout messages.",
            type=Path,
        )

        file_types_group = parser.add_mutually_exclusive_group()
        file_types_group.add_argument(
            "--exclude",
            action="append",
            help="specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files",
            type=str,
        )
        file_types_group.add_argument(
            "--include",
            action="append",
            help="specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot be set if excluding files",
            type=str,
        )
        return parser

    def generate_config(self) -> models.Config:
        if self.args.config:
            with self.args.config.open("r") as json_conf:
                conf = json.load(json_conf)
        else:
            conf = dict()

        for arg, value in vars(self.args).items():
            if arg == "config" or arg in conf.keys():
                continue
            conf[arg] = value

        cfg = models.Config(
            root=conf["directory"],
            is_verbose=conf["verbose"],
            include_gitignore=conf["include_gitignore"],
            include_dotfiles=conf["include_dotfiles"],
            include_symlinks=conf["include_symlinks"],
            include_images=conf["include_images"],
            model=conf["model"],
            json_destination=conf["json"],
            exclude=conf["exclude"],
            include=conf["include"],
        )
        return cfg

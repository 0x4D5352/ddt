import json
from typing import Any
from ddt import models
from pathlib import Path
import argparse

"""
Scanner Base Class
"""


class Scanner:
    def __init__(
        self,
        directory_path: Path,
        is_verbose: bool,
        include_gitignore: bool,
        include_dotfiles: bool,
        include_symlinks: bool,
        include_images: bool,
        model: models.Model,
        json_destination: Path,
        exclude: list[str],
        include: list[str],
    ) -> None:
        self.directory_path: Path = directory_path
        self.is_verbose: bool = is_verbose
        self.include_gitignore: bool = include_gitignore
        self.include_dotfiles: bool = include_dotfiles
        self.include_symlinks: bool = include_symlinks
        self.include_images: bool = include_images
        self.model: models.Model = model
        self.json_destination: Path = json_destination
        self.exclude: list[str] = exclude
        self.include: list[str] = include


"""
CLI Arg Parser
"""


# TODO: consider just making this a function instead of a subclass
class CLI(Scanner):
    def __init__(self) -> None:
        parser = self.setup_argparse()
        args = parser.parse_args()
        if args.config:
            print("got a config!")
            pass
        super().__init__(
            args.directory,
            args.verbose,
            args.include_gitignore,
            args.include_dotfiles,
            args.include_symlinks,
            args.include_images,
            args.model,
            args.json,
            args.exclude,
            args.include,
        )

    def setup_argparse(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="Tokenizer",
            description="Crawls a given directory, counts the number of tokens per filetype in the project and returns a per-type total and grand total",
            epilog="Made with <3 by 0x4D5352",
        )

        inputs = parser.add_mutually_exclusive_group()
        inputs.add_argument(
            "directory",
            help="the relative or absolute path to the directory you wish to scan",
            type=Path,
        )
        inputs.add_argument(
            "--config",
            help="the relative or absolute path towards the configuration file. excluded CLI flags will be replaced with defaults",
            type=Path,
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


"""
JSON file parser
"""


# TODO: consider making this just a function, not a subclass
class JSON(Scanner):
    def __init__(self) -> None:
        # TODO: parse a json input file
        directory_path = Path()
        is_verbose = False
        include_gitignore = False
        include_dotfiles = False
        include_symlinks = False
        include_images = False
        model = models.GPT_4O
        json_destination = Path()
        exclude = [""]
        include = [""]
        super().__init__(
            directory_path,
            is_verbose,
            include_gitignore,
            include_dotfiles,
            include_symlinks,
            include_images,
            model,
            json_destination,
            exclude,
            include,
        )

    def parse_config_file(self):
        pass


"""
Output methods
"""


class TokenEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, models.TokenCounter) or isinstance(o, models.FileCategory):
            return o._to_dict()
        return super().default(o)


def output_as_json(token_counter: models.TokenCounter, file: Path) -> None:
    with file.open("w") as f:
        json.dump(token_counter, f, cls=TokenEncoder, indent=2)

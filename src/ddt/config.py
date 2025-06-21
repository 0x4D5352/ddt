import logging
from pathlib import Path
from typing import Any, TextIO
from dataclasses import dataclass, field
from . import tokenizer

"""
Config model
"""


@dataclass
class Config:
    """
    A class representing the configuration for the current run of DDT. 

    Properties:
        root (Path): The starting directory for the path traversal.
        is_verbose (bool): Verbosity flag - True logs DEBUG output.
        include_gitignore (bool): Flag - True counts tokens of gitignored files.
        include_dotfiles (bool): Flag - True counts tokens of dotfiles and dotfile directories.
        include_symlinks (bool): Flag - True counts tokens of symbolically linked files.
        include_images (bool): Flag - True counts image tokens.
        resolve_paths (bool): Flag - True displays file names by their absolute path.
        model (Model): The specified model for the encoding algorithms.
        output (TextIO): The output stream for results.
        output_format (str): The output encoding format.
        exclude (list[str]): The list of user-specified filetypes to exclude
        include (list[str]): The list of user-specified filetypes to include - all other types are ignored.
        gitignore (set[Path]): The files found within the gitignore.
    """
    root: Path
    is_verbose: bool
    include_gitignore: bool
    include_dotfiles: bool
    include_symlinks: bool
    include_images: bool
    resolve_paths: bool
    model: tokenizer.Model
    output: TextIO
    output_format: str
    exclude: list[str]
    include: list[str]
    gitignore: set[Path] = field(init=False)

    def __post_init__(self):
        self.gitignore = self._parse_gitignore()
        self._setup_logging()

    # AI rewrote this function for me, need to replace.
    def _parse_gitignore(self) -> set[Path]:
        # TODO: implement https://github.com/cpburnz/python-pathspec for gitignore and rewrite from scratch. or maybe its fine to just keep?
        """
        Reads the .gitignore file in the given root directory, interprets its patterns,
        and returns a set of Paths representing all files and directories within root that match
        those patterns. Lines that are empty or start with '#' (comments) are ignored.

        For pattern matching:
          - Patterns that start with '/' are treated as relative to the root.
          - Patterns that contain a slash (but do not start with '/') are also treated as relative.
          - Patterns without any slash are searched recursively using rglob.
          - If a pattern ends with '/', it is interpreted as a directory (the trailing slash is removed
            before matching).

        Args:
            root (Path): The root directory containing the .gitignore file.

        Returns:
            Set[Path]: A set of Paths that match the patterns specified in the .gitignore file.
        """
        ignored: set[Path] = set()
        gitignore_file: Path = self.root / ".gitignore"

        try:
            with gitignore_file.open("r") as f:
                patterns = []
                for line in f:
                    stripped = line.strip()
                    # Skip empty lines or comments.
                    if not stripped or stripped.startswith("#"):
                        continue
                    patterns.append(stripped)
        except FileNotFoundError:
            return ignored  # No .gitignore file found.

        for pattern in patterns:
            # Check if the pattern is meant for directories (ends with a slash)
            if pattern.endswith("/"):
                # Remove trailing slash for glob matching.
                pattern = pattern.rstrip("/")

            # If the pattern starts with '/', it is anchored to the root.
            if pattern.startswith("/"):
                # Remove the leading slash.
                pattern = pattern[1:]
                # Use glob relative to the root (non-recursive).
                matches = self.root.glob(pattern)
            # If the pattern contains a slash somewhere, treat it as relative to the root.
            elif "/" in pattern:
                matches = self.root.glob(pattern)
            else:
                # Pattern without a slash: search recursively.
                matches = self.root.rglob(pattern)

            for match in matches:
                ignored.add(match)

        return ignored

    def _setup_logging(self) -> None:
        level = logging.DEBUG if self.is_verbose else logging.INFO
        logging.basicConfig(format='%(message)s', level=level)

def generate_config(args: dict[str, Any]) -> Config:
    """
    Basically the main function of this class - it converts the CLI config into a system config:

    - Fills out config with existing config file.
    - Specifies output format.
    - applies CLI args to config
    - Resolves the root path and validates that it is a directory
    - Generates and returns a config based on the CLI and JSON config
    """
    if args["json"]:
        output_format = "json"
    elif args["html"]:
        output_format = "html"
    else:
        output_format = "txt"

    cfg = Config(
        root=args["directory"].resolve(),
        is_verbose=args["verbose"],
        include_gitignore=args["include_gitignore"],
        include_dotfiles=args["include_dotfiles"],
        include_symlinks=args["include_symlinks"],
        include_images=args["include_images"],
        resolve_paths=args["resolve_paths"],
        model=args["model"],
        output=args["output"],
        output_format=output_format,
        exclude=args["exclude"],
        include=args["include"],
    )
    return cfg

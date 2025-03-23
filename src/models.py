import mimetypes
from pathlib import Path
from typing import NewType, Any, TextIO
from dataclasses import dataclass, field
from . import tokenizer, logging
from PIL import Image
import json

"""
type aliasing for convenince
"""

Model = NewType("Model", str)
GPT_4O: Model = Model("gpt-4o")
GPT_4O_MINI: Model = Model("gpt-4o-mini")
GPT_4_TURBO: Model = Model("gpt-4-turbo")
GPT_4: Model = Model("gpt-4")

MODEL_CHOICES: set[Model] = set([GPT_4O, GPT_4O_MINI, GPT_4_TURBO, GPT_4])

"""
Config model
"""


@dataclass
class Config:
    root: Path
    is_verbose: bool
    include_gitignore: bool
    include_dotfiles: bool
    include_symlinks: bool
    include_images: bool
    resolve_paths: bool
    model: Model
    output: TextIO
    output_format: str
    exclude: list[str]
    include: list[str]
    gitignore: set[Path] = field(init=False)

    def __post_init__(self):
        self.gitignore = self.parse_gitignore()

    # AI rewrote this function for me, need to replace.
    def parse_gitignore(self) -> set[Path]:
        # TODO: implement https://github.com/cpburnz/python-pathspec for gitignore and rewrite from scratch
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


"""
Data models
"""


class TokenCounter:
    """
    A class representing the contents of a directory and the count of tokens per file in that directory.

    Args:
        root(Path): The root path of the directory.
        all_files(list[Path]): All file paths in the directory.
        ignored_files(dict[str, list[Path]]): All files ignored by the scan, grouped by extension.
        scanned_files(dict[str, FileCategory]): All files scanned, grouped by extension.
        excluded_files(set[Path]): All files to be excluded from the search.
        included_files(set[Path]): All files to be included in the search.
        total(int): The total number of tokens present within the directory.
        config(Config): the configuration file for the TokenCounter being run.
    """

    def __init__(self, cfg: Config) -> None:
        mimetypes.init()
        self.config: Config = cfg
        if self.config.resolve_paths:
            self.all_files: list[Path] = [
                file.resolve() for file in self.config.root.glob("**/*.*")
            ]
        else:
            self.all_files: list[Path] = [
                file for file in self.config.root.glob("**/*.*")
            ]
        self.ignored_files: dict[str, list[Path]] = {}
        self.scanned_files: dict[str, FileCategory] = {}
        self.excluded_files: set[Path] = set()
        self.included_files: set[Path] = set()
        self.total: int = 0

    def _to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.config.root),
            "all_files": [path.name for path in self.all_files],
            "ignored_files": {
                key: [path.name for path in paths]
                for key, paths in self.ignored_files.items()
            },
            "scanned_files": {
                ext: category._to_dict() for ext, category in self.scanned_files.items()
            },
            "total": self.total,
        }

    def _to_text(self) -> str:
        result: str = "totals:\n"
        result += "-------------------------\n"
        for extension, file_extension in self.scanned_files.items():
            result += f"{extension} tokens:\n"
            result += "*************************\n"
            for file in file_extension.files:
                result += f"{file['file']}: {file['tokens']:,} tokens\n"
            result += ".........................\n"
            result += (
                f"{file_extension.extension} total: {file_extension.total:,} tokens\n"
            )
            result += "_________________________\n"

        result += "-------------------------\n"
        result += f"grand total: {self.total:,}\n"
        result += (
            f"remaining tokens given 128K context window: {128_000 - self.total:,}\n"
        )
        return result

    def add_exclusions(self, exclusions: list[str]) -> None:
        if exclusions is None or len(exclusions) < 1:
            return
        for ext in exclusions:
            for file in self.config.root.glob(f"**/*.{ext}"):
                self.excluded_files.add(file.resolve())

    def add_inclusions(self, inclusions: list[str]) -> None:
        if inclusions is None or len(inclusions) < 1:
            return
        for ext in inclusions:
            for file in self.config.root.glob(f"**/*.{ext}"):
                self.included_files.add(file.resolve())

    def count_text_file(self, file: Path, file_extension: str) -> int:
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            if file_extension not in self.ignored_files:
                self.ignored_files[file_extension] = []
            self.ignored_files[file_extension].append(file)
            logging.print_if_verbose(
                f"file {file.name} hit unicode error, ignoring", self.config.is_verbose
            )
            return 0
        return tokenizer.calculate_text_tokens(text, self.config.model)

    def count_image_file(self, file: Path, file_extension: str) -> int:
        try:
            img = Image.open(file)
            return tokenizer.calculate_image_tokens(*img.size)
        except Exception as e:
            if file_extension not in self.ignored_files:
                self.ignored_files[file_extension] = []
            self.ignored_files[file_extension].append(file)
            logging.print_if_verbose(
                f"file {file.name} hit error {e}, ignoring", self.config.is_verbose
            )
            return 0

    def parse_files(self):
        for file in self.all_files:
            logging.print_if_verbose(f"checking {str(file)}", self.config.is_verbose)
            if file.is_dir():
                continue
            file_extension = self.grab_suffix(file)
            mime: str | None = (
                mimetypes.types_map[file_extension]
                if file_extension in mimetypes.types_map
                else None
            )

            def add_to_ignored(file: Path, filetype: str):
                logging.print_if_verbose(
                    f"ignoring {str(file)}", self.config.is_verbose
                )
                if filetype not in self.ignored_files:
                    self.ignored_files[filetype] = []
                self.ignored_files[filetype].append(file)

            if len(self.included_files) > 0 and file not in self.included_files:
                add_to_ignored(file, file_extension)
                continue

            if len(self.excluded_files) > 0 and file in self.excluded_files:
                add_to_ignored(file, file_extension)
                continue

            if not self.config.include_dotfiles and any(
                part.startswith(".") for part in file.parts
            ):
                add_to_ignored(file, file_extension)
                continue

            if not self.config.include_gitignore and file in self.config.gitignore:
                add_to_ignored(file, file_extension)
                continue

            if (
                not self.config.include_symlinks
                and self.config.root.name not in file.resolve().parts
            ):
                add_to_ignored(file, file_extension)
                continue

            logging.print_if_verbose(f"reading {str(file)}", self.config.is_verbose)

            if mime:
                category = mime.split("/")[0]
                match category:
                    case "image":
                        if self.config.include_images:
                            token_counts = self.count_image_file(file, file_extension)
                        else:
                            add_to_ignored(file, file_extension)
                            continue
                    case _:
                        # currently assuming everything is a text file if it's not an image
                        token_counts = self.count_text_file(file, file_extension)
            else:
                token_counts = self.count_text_file(file, file_extension)

            if file_extension not in self.scanned_files:
                self.scanned_files[file_extension] = FileCategory(file_extension)
            self.scanned_files[file_extension].files.append(
                {"file": file.name, "tokens": token_counts}
            )
            self.scanned_files[file_extension].total += token_counts
            self.total += token_counts

    def grab_suffix(self, file: Path) -> str:
        if len(file.suffixes) == 1:
            return file.suffix
        result = ""
        for suffix in file.suffixes:
            result += suffix
        return result

    def output(self) -> None:
        if not self.config.output:
            print("how did you get past the guard clause when calling this")
            return
        with self.config.output as f:
            match self.config.output_format:
                case "json":
                    json.dump(self, f, cls=TokenEncoder, indent=2)
                case _:
                    f.write(self._to_text())


class FileCategory:
    def __init__(self, extension: str) -> None:
        self.extension: str = extension
        self.files: list[dict[str, str | int]] = []
        self.total: int = 0

    def _to_dict(self):
        return {
            "total": self.total,
            "files": self.files,
        }


class TokenEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, TokenCounter) or isinstance(o, FileCategory):
            return o._to_dict()
        return super().default(o)

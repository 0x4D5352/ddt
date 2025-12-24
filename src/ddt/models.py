import mimetypes
import logging
from pathlib import Path
from typing import Any
from typing import override as orr
from . import tokenizer
from .config import Config
from PIL import Image
from jinja2 import Environment, PackageLoader, select_autoescape
import json

"""
Data models
"""


class TokenCounter:
    """
    A class representing the contents of a directory and the count of tokens per file in that directory.

    Attributes:
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
        self.all_files: list[Path] = (
            [file.resolve() for file in self.config.root.glob("**/*.*")]
            if self.config.resolve_paths
            else [file for file in self.config.root.glob("**/*.*")]
        )
        self.ignored_files: dict[str, list[Path]] = {}
        self.scanned_files: dict[str, FileCategory] = {}
        self.excluded_files: set[Path] = set()
        self.included_files: set[Path] = set()
        self.total: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Converts TokenCounter to a dictionary type for JSON encoding.
        """
        return {
            "root": str(self.config.root),
            "all_files": [path.name for path in self.all_files],
            "ignored_files": {
                key: [path.name for path in paths]
                for key, paths in self.ignored_files.items()
            },
            "scanned_files": {
                ext: category.to_dict() for ext, category in self.scanned_files.items()
            },
            "total": self.total,
        }

    def to_text(self) -> str:
        """
        Converts TokenCounter to an ASCII-style table.
        """
        result: str = ""
        if self.config.is_verbose:
            result += "ignored:\n"
            for extension, ignored in self.ignored_files.items():
                result += "=========================\n"
                result += f"{extension} files ignored:\n"
                result += "*************************\n"
                for file in ignored:
                    result += f"{str(file)}\n"
            result += "=========================\n"
        result += "totals:\n"
        for extension, file_extension in self.scanned_files.items():
            result += "-------------------------\n"
            result += f"{extension} tokens:\n"
            result += "*************************\n"
            for file in file_extension.files:
                result += f"{file['file']}: {file['tokens']:,} tokens\n"
            result += ".........................\n"
            result += (
                f"{file_extension.extension} total: {file_extension.total:,} tokens\n"
            )

        result += "-------------------------\n"
        result += f"grand total: {self.total:,}\n"
        result += (
            f"remaining tokens given 128K context window: {128_000 - self.total:,}\n"
        )
        return result

    def to_html(self) -> str:
        """
        Converts TokenCounter to an HTML table.
        """
        env = Environment(loader=PackageLoader("ddt"), autoescape=select_autoescape())
        template = env.get_template("template.html")
        values: dict[
            str, Path | bool | dict[str, list[Path]] | dict[str, FileCategory] | int
        ] = {
            "directory": self.config.root,
            "verbose": self.config.is_verbose,
            "ignored_files": self.ignored_files,
            "scanned_files": self.scanned_files,
            "total": self.total,
        }
        result: str = template.render(values)
        return result

    def add_exclusions(self, exclusions: list[str]) -> None:
        """
        Adds filetypes to the excluded files list.

        Args:
            exclusions (list[str]): The file extensions to be excluded.
        """
        if exclusions is None or len(exclusions) < 1:
            return
        for ext in exclusions:
            for file in self.config.root.glob(f"**/*.{ext}"):
                self.excluded_files.add(file.resolve())

    def add_inclusions(self, inclusions: list[str]) -> None:
        """
        Adds files to the included files list.

        Args:
            inclusions (list[str]): The file extensions to be included.
        """
        if inclusions is None or len(inclusions) < 1:
            return
        for ext in inclusions:
            for file in self.config.root.glob(f"**/*.{ext}"):
                self.included_files.add(file.resolve())

    def count_text_file(self, file: Path) -> int:
        """
        Parses the given text file and return the total number of tokens.

        Args:
            file (Path): The text file being processed
            file_extension (str): The suffix of the filetype.

        Returns:
            int: the total number of tokens in the file.
        """
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            logging.debug(f"file {file.name} hit unicode error, ignoring")
            self.add_to_ignored(file)
            return 0
        return tokenizer.calculate_text_tokens(text, self.config.model)

    def count_image_file(self, file: Path) -> int:
        """
        Parses the given image file and return the total number of tokens.

        Args:
            file (Path): The text image being processed
            file_extension (str): The suffix of the filetype.

        Returns:
            int: the total number of tokens in the file.
        """
        try:
            img = Image.open(file)
            width, height = img.size
            return tokenizer.calculate_image_tokens(width, height)
        except Exception as e:
            logging.debug(f"file {file.name} hit error {e}, ignoring")
            self.add_to_ignored(file)
            return 0

    def add_to_ignored(self, file: Path):
        """
        Adds the given file to the ignored files list.
        """
        filetype = self.grab_suffix(file)
        logging.debug(f"ignoring {str(file)}")
        if filetype not in self.ignored_files:
            self.ignored_files[filetype] = []
        self.ignored_files[filetype].append(file)

    def filter_file(self, file: Path) -> bool:
        if len(self.included_files) > 0 and file not in self.included_files:
            self.add_to_ignored(file)
            return True

        if len(self.excluded_files) > 0 and file in self.excluded_files:
            self.add_to_ignored(file)
            return True

        if not self.config.include_dotfiles and any(
            part.startswith(".") for part in file.parts
        ):
            self.add_to_ignored(file)
            return True

        if not self.config.include_gitignore and file in self.config.gitignore:
            self.add_to_ignored(file)
            return True

        if (
            not self.config.include_symlinks
            and self.config.root.name not in file.resolve().parts
        ):
            self.add_to_ignored(file)
            return True

        return False

    def parse_file(self, file: Path) -> tuple[str, int]:
        """
        Parses an individual file. Checks the MIME, and
        """
        file_extension = self.grab_suffix(file)

        # TODO: start subdividing by mimetypes and set up your own mimetype list
        # file_type = mimetypes.guess_file_type(file)
        # logging.debug(f"filetype guess: {file_type}")
        mime: str | None = (
            mimetypes.types_map[file_extension]
            if file_extension in mimetypes.types_map
            else None
        )

        logging.debug(f"reading {str(file)}")

        if mime:
            category = mime.split("/")[0]
            match category:
                case "image":
                    if self.config.include_images:
                        token_counts = self.count_image_file(file)
                    else:
                        self.add_to_ignored(file)
                        return "", -1
                case _:
                    # currently assuming everything is a text file if it's not an image
                    token_counts = self.count_text_file(file)
        else:
            token_counts = self.count_text_file(file)
        return file_extension, token_counts

    def parse_files(self):
        """
        Iterate through `self.all_files`, skip uncounted files, and parse the rest.
        Anything that didn't result in a token count is skipeped, and the rest are added
        to the list of scanned files.

        """
        for file in self.all_files:
            logging.debug(f"checking {str(file)}")
            if file.is_dir():
                continue

            filtered: bool = self.filter_file(file)
            if filtered:
                continue

            file_extension, token_counts = self.parse_file(file)

            if token_counts < 0:
                continue

            if file_extension not in self.scanned_files:
                self.scanned_files[file_extension] = FileCategory(file_extension)
            self.scanned_files[file_extension].files.append(
                {"file": file.name, "tokens": token_counts}
            )
            self.scanned_files[file_extension].total += token_counts
            self.total += token_counts

    def grab_suffix(self, file: Path) -> str:
        """
        A helper module to handle the cases where a filetype has multiple periods in the extension, e.g. .tar.gz

        Args:
            file (Path): The file path

        Returns:
            str: the full file path.
        """
        if len(file.suffixes) == 1:
            return file.suffix
        result = ""
        for suffix in file.suffixes:
            result += suffix
        return result

    def output(self) -> None:
        """
        Writes the contents of the tokenencoder to the eoutput.
        """
        if not self.config.output:
            exit(1)
        with self.config.output as f:
            match self.config.output_format:
                case "json":
                    json.dump(self, f, cls=TokenCounterEncoder, indent=2)
                case "html":
                    _ = f.write(self.to_html())
                case _:
                    _ = f.write(self.to_text())


class TokenCounterEncoder(json.JSONEncoder):
    """
    A custom token encoder that overrides the default() method to allow encoding of the TokenCounter to JSON
    """

    # was having some issues with the @override decorator, this is a workaround
    @orr
    def default(self, o: Any) -> Any:
        if isinstance(o, TokenCounter) or isinstance(o, FileCategory):
            return o.to_dict()
        return super().default(o)


class FileCategory:
    """
    A class representing a particular type of file, like a .txt or .yaml.

    Args:
    extension: str - The file extension, e.g. .txt

    Attributes:
    extension: str - The file extension, e.g. .txt
    files: list[dict[str, str | int]] - The files, with the structure {"file": str, "tokens": int}
    tital: int - the total number of tokens in this file category.

    """

    def __init__(self, extension: str) -> None:
        self.extension: str = extension
        self.files: list[dict[str, str | int]] = []
        self.total: int = 0

    def to_dict(self):
        """
        Converts TokenCounter to a dictionary type for JSON encoding.
        """
        return {
            "total": self.total,
            "files": self.files,
        }

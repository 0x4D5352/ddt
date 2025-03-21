from pathlib import Path
from typing import NewType
from . import tokenizer
from PIL import Image

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
        total(int): The total number of tokens present within the directory.
    """

    def __init__(self, root: Path, model: Model) -> None:
        self.root: Path = root
        # TODO: make all the .resolve() calls optional
        self.all_files: list[Path] = [file.resolve() for file in root.glob("**/*.*")]
        self.ignored_files: dict[str, list[Path]] = {}
        self.scanned_files: dict[str, FileCategory] = {}
        self.excluded_files: set[Path] = set()
        self.included_files: set[Path] = set()
        self.gitignore: set[Path] = self.parse_gitignore(root)
        self.total: int = 0
        self.model = model

    def _to_dict(self):
        return {
            "root": str(self.root),
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

    def add_exclusions(self, exclusions: list[str]) -> None:
        if exclusions is None or len(exclusions) < 1:
            return
        for ext in exclusions:
            for file in self.root.glob(f"**/*.{ext}"):
                self.excluded_files.add(file.resolve())

    def add_inclusions(self, inclusions: list[str]) -> None:
        if inclusions is None or len(inclusions) < 1:
            return
        for ext in inclusions:
            for file in self.root.glob(f"**/*.{ext}"):
                self.included_files.add(file.resolve())

    def count_text_file(self, file: Path, file_extension: str) -> int:
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            if file_extension not in self.ignored_files:
                self.ignored_files[file_extension] = []
            self.ignored_files[file_extension].append(file)
            print(f"file {file.name} hit unicode error, ignoring")
            return 0
        return tokenizer.calculate_text_tokens(text, self.model)

    def count_image_file(self, file: Path, file_extension: str) -> int:
        img = Image.open(file)
        width = img.width
        height = img.height
        return tokenizer.calculate_image_tokens(width, height)

    # TODO: implement https://github.com/cpburnz/python-pathspec for gitignore and rewrite from scratch
    # AI wrote this code.
    def parse_gitignore(self, root: Path) -> set[Path]:
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
        gitignore_file: Path = root / ".gitignore"

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
                matches = root.glob(pattern)
            # If the pattern contains a slash somewhere, treat it as relative to the root.
            elif "/" in pattern:
                matches = root.glob(pattern)
            else:
                # Pattern without a slash: search recursively.
                matches = root.rglob(pattern)

            for match in matches:
                ignored.add(match)

        return ignored


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

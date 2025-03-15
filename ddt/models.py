from pathlib import Path

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

    def __init__(self, root: Path, all_files: list[Path]) -> None:
        self.root: Path = root
        self.all_files: list[Path] = all_files
        self.ignored_files: dict[str, list[Path]] = {}
        self.scanned_files: dict[str, FileCategory] = {}
        self.total: int = 0

    def to_dict(self):
        return {
            "root": str(self.root),
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


class FileCategory:
    def __init__(self, extension: str) -> None:
        self.extension: str = extension
        self.files: list[dict[str, str | int]] = []
        self.total: int = 0

    def to_dict(self):
        return {
            "total": self.total,
            "files": self.files,
        }

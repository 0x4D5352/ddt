import shutil
import sys
from pathlib import Path
from typing import TextIO
import pytest
from ddt import config
from ddt.tokenizer import Model


@pytest.fixture
def test_directory(tmp_path):
    """
    Create a temporary copy of test_files directory.

    This fixture copies the tests/test_files directory to a temporary location
    for isolated testing. Symlinks are not followed to match the original
    test behavior where symlinked files would be filtered out.
    """
    source = Path("tests/test_files")
    dest = tmp_path / "test_files"

    if source.exists():
        # Use ignore function to skip symlinks during copy
        def ignore_symlinks(dir, files):
            return [f for f in files if (Path(dir) / f).is_symlink()]

        shutil.copytree(source, dest, ignore=ignore_symlinks)
    else:
        # Create minimal test structure if source doesn't exist
        dest.mkdir()
        (dest / "testfile.txt").write_text(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )

    return dest


@pytest.fixture
def base_config():
    """
    Factory fixture for creating test configs with sensible defaults.

    Usage:
        def test_something(base_config, tmp_path):
            cfg = base_config(root=tmp_path, include_images=True)
    """

    def _make_config(
        root: Path | None = None,
        is_verbose: bool = True,
        include_gitignore: bool = False,
        include_dotfiles: bool = False,
        include_symlinks: bool = False,
        include_images: bool = False,
        resolve_paths: bool = False,
        model: Model | None = None,
        output: TextIO | None = None,
        output_format: str = "txt",
        exclude: list[str] | None = None,
        include: list[str] | None = None,
    ) -> config.Config:
        return config.Config(
            root=root if root is not None else Path("."),
            is_verbose=is_verbose,
            include_gitignore=include_gitignore,
            include_dotfiles=include_dotfiles,
            include_symlinks=include_symlinks,
            include_images=include_images,
            resolve_paths=resolve_paths,
            model=model if model is not None else Model("gpt-4o"),
            output=output if output is not None else sys.stdout,
            output_format=output_format,
            exclude=exclude or [],
            include=include or [],
        )

    return _make_config

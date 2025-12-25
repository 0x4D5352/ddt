import shutil
import sys
from pathlib import Path
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

    def _make_config(**overrides):
        defaults = {
            "root": Path("."),
            "is_verbose": True,
            "include_gitignore": False,
            "include_dotfiles": False,
            "include_symlinks": False,
            "include_images": False,
            "resolve_paths": False,
            "model": Model("gpt-4o"),
            "output": sys.stdout,
            "output_format": "txt",
            "exclude": [],
            "include": [],
        }
        defaults.update(overrides)
        return config.Config(**defaults)

    return _make_config

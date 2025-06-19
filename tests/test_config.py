from pathlib import Path
import sys
from ddt import config, tokenizer


def test_config_happy_path():
    root = Path(".")
    is_verbose = True
    include_gitignore = True
    include_dotfiles = True
    include_symlinks = True
    include_images = True
    resolve_paths = True
    model = tokenizer.Model("gpt-4o")
    output = sys.stdout
    output_format = "txt"
    exclude = ["foo"]
    include = ["bar"]

    cfg = config.Config(
        root, 
        is_verbose,
        include_gitignore,
        include_dotfiles,
        include_symlinks,
        include_images,
        resolve_paths,
        model,
        output,
        output_format,
        exclude,
        include)



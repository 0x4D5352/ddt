import os
from pathlib import Path
from ddt import cli, tokenizer

"""
def test_parser_greet_args():
    parser = build_parser()
    args = parser.parse_args(["greet", "Alice"])

    assert args.command == "greet"
    assert args.name == "Alice"
    assert args.func == handle_greet
"""


def test_directory_arg():
    parser = cli.setup_argparse()
    args = parser.parse_args(["src"])
    assert args.root == Path("src")

def test_verbosity_arg():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--verbose", "src"])
    assert args.verbose

def test_includes_args():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--include-gitignore", "--include-dotfiles", "--include-symlinks", "--include-images", "src"])
    assert args.include_gitignore
    assert args.include_dotfiles
    assert args.include_symlinks
    assert args.include_images

def test_resolve_paths_arg():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--resolve-paths", "src"])
    assert args.resolve_paths

def test_model_choices_arg():
    for model in tokenizer.MODEL_CHOICES:
        parser = cli.setup_argparse()
        args = parser.parse_args(["--model", model, "src"])
        assert args.model == model

def test_output_arg():
    parser = cli.setup_argparse()
    with open("test.txt", "w") as file:
        args = parser.parse_args(["--output", "test.txt", "src"])
        assert args.output.name == file.name
        length = args.output.write("foo")
        assert length == 3
        os.remove(file.name)

def test_output_json_arg():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--json", "src"])
    assert args.json

def test_output_html_arg():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--html", "src"])
    assert args.html

def test_exclude_args():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--exclude", ".py", "src"])
    assert args.exclude == [".py"]

def test_include_args():
    parser = cli.setup_argparse()
    args = parser.parse_args(["--include", ".py", "src"])
    assert args.include == [".py"]


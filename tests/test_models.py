import os
from pathlib import Path
import sys
from ddt import config, models
from ddt.tokenizer import Model

"""
    token counter
"""


def test_tokencounter_init():
    cfg = config.Config(
        Path("."),
        False,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    assert tc.config == cfg
    assert tc.all_files == [file for file in Path(".").glob("**/*.*")]
    assert tc.ignored_files == dict()
    assert tc.scanned_files == dict()
    assert tc.excluded_files == set()
    assert tc.included_files == set()
    assert tc.total == 0


def test_tokencounter_to_dict():
    cfg = config.Config(
        Path("."),
        False,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    result = tc.to_dict()
    assert result["root"] == str(Path("."))
    assert result["all_files"] == [file.name for file in Path(".").glob("**/*.*")]
    assert result["ignored_files"] == dict()
    assert result["scanned_files"] == dict()
    assert result["total"] == 0


def test_tokencounter_to_text():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    result = tc._to_text()
    assert "=========================\n" in result
    assert "ignored:" in result
    assert "total:" in result


def test_tokencounter_to_html():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    result = tc._to_html()
    assert "<!DOCTYPE html>" in result
    assert "Scanned files in" in result
    assert "<table>" in result
    assert "</table>" in result
    assert '<th scope="row">Grand Total</th>' in result


def test_tokencounter_add_exclusions():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    exclusions = ["lock"]
    tc.add_exclusions(exclusions)
    assert tc.excluded_files == {Path("uv.lock").resolve()}


def test_tokencounter_add_inclusions():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    inclusions = ["lock"]
    tc.add_inclusions(inclusions)
    assert tc.included_files == {Path("uv.lock").resolve()}


def test_tokencounter_count_text_file():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    count = tc.count_text_file(Path("assets/demo.tape"))
    assert count == 830


def test_tokencounter_count_image_file():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    count = tc.count_image_file(Path("assets/demo.gif"))
    assert count == 1105


def test_tokencounter_add_to_ignored():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    file = Path("README.md")
    tc.add_to_ignored(file)
    assert file in tc.ignored_files[".md"]


def test_tokencounter_filter_file():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)

    inclusions = ["py"]
    tc.add_inclusions(inclusions)
    not_included = Path("README.md")
    filtered = tc.filter_file(not_included)
    assert filtered
    assert tc.ignored_files[".md"] == [not_included]
    tc.included_files = set()
    tc.ignored_files = dict()

    exclusions = ["lock"]
    tc.add_exclusions(exclusions)
    excluded_file = Path("uv.lock")
    filtered = tc.filter_file(excluded_file)
    assert filtered
    assert tc.ignored_files[".lock"] == [excluded_file]
    tc.excluded_files = set()
    tc.ignored_files = dict()

    # dotfiles
    dotfile = Path(".gitignore")
    filtered = tc.filter_file(dotfile)
    assert filtered
    assert [dotfile] in tc.ignored_files.values()
    tc.ignored_files = dict()

    # gitignore
    # TODO: replace with pytest temp dir stuff
    with open("gitignored.json", "w") as file:
        _ = file.write('{"foo": "bar"}')
    gitignored = Path("gitignored.json")
    filtered = tc.filter_file(gitignored)
    assert filtered
    assert tc.ignored_files[".json"] == [gitignored]
    tc.ignored_files = dict()
    os.remove(gitignored)

    # symlinks
    symlinked = Path("tests/test_files/README.md")
    filtered = tc.filter_file(symlinked)
    assert filtered
    assert tc.ignored_files[".md"] == [symlinked]


def test_tokencounter_parse_file():
    cfg = config.Config(
        Path("."),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    file = Path("tests/test_files/testfile.txt")
    extension, token_count = tc.parse_file(file)
    assert extension == ".txt"
    assert token_count == 22


def test_tokencounter_parse_files():
    cfg = config.Config(
        Path("assets"),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    tc.parse_files()
    assert tc.ignored_files[".png"] == [
        Path("assets/contextwindow.png"),
        Path("assets/beemovie.png"),
    ]
    assert tc.ignored_files[".gif"] == [Path("assets/demo.gif")]

    assert tc.scanned_files[".tape"].files == [
        {"file": Path("assets/demo.tape").name, "tokens": 830}
    ]
    assert tc.total == 830


def test_tokencounter_grab_suffix():
    cfg = config.Config(
        Path("assets"),
        True,
        False,
        False,
        False,
        False,
        False,
        Model("gpt-4o"),
        sys.stdout,
        "txt",
        [],
        [],
    )
    tc = models.TokenCounter(cfg)
    file = Path("README.md")
    suffix = tc.grab_suffix(file)
    assert suffix == ".md"
    # TODO: replace with pytest temp dir stuff
    with open("foobar.tar.gz", "w") as f:
        _ = f.write("hello mom")
    file = Path("foobar.tar.gz")
    suffix = tc.grab_suffix(file)
    assert suffix == ".tar.gz"
    os.remove(file)


def test_tokencounter_txt_output():
    # TODO: replace with pytest temp dir stuff
    with open("foo.txt", "w") as file:
        cfg = config.Config(
            Path("assets"),
            True,
            False,
            False,
            False,
            False,
            False,
            Model("gpt-4o"),
            file,
            "txt",
            [],
            [],
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()
    with open("tests/test_files/output.txt", "r") as f:
        with open("foo.txt", "r") as file:
            assert file.read() == f.read()
    os.remove(Path("foo.txt"))


# This covers the TokenCounterEncoder too, technically - it only exists in output()
def test_tokencounter_json_output():
    # TODO: replace with pytest temp dir stuff
    with open("foo.json", "w") as file:
        cfg = config.Config(
            Path("assets"),
            True,
            False,
            False,
            False,
            False,
            False,
            Model("gpt-4o"),
            file,
            "json",
            [],
            [],
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()
    with open("tests/test_files/output.json", "r") as f:
        with open("foo.json", "r") as file:
            assert file.read() == f.read()
    os.remove(Path("foo.json"))


def test_tokencounter_html_output():
    # TODO: replace with pytest temp dir stuff
    with open("foo.html", "w") as file:
        cfg = config.Config(
            Path("assets"),
            True,
            False,
            False,
            False,
            False,
            False,
            Model("gpt-4o"),
            file,
            "html",
            [],
            [],
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()
    with open("tests/test_files/output.html", "r") as f:
        with open("foo.html", "r") as file:
            assert file.read() == f.read()
    os.remove(Path("foo.html"))


"""
    filecategory
"""


def test_filecategory():
    fc = models.FileCategory(".foo")
    assert fc.extension == ".foo"
    assert fc.files == []
    assert fc.total == 0
    assert fc.to_dict() == {"total": 0, "files": []}

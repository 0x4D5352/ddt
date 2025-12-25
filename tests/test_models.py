import json
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
    result = tc.to_text()
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
    result = tc.to_html()
    assert "<!DOCTYPE html>" in result
    assert "Scanned files in" in result
    assert "<table>" in result
    assert "</table>" in result
    assert '<th scope="row">Grand Total</th>' in result


def test_tokencounter_add_exclusions():
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
    tc.add_exclusions([])
    assert tc.included_files == set()
    exclusions = ["tape"]
    tc.add_exclusions(exclusions)
    assert tc.excluded_files == {Path("assets/demo.tape").resolve()}


def test_tokencounter_add_inclusions():
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
    tc.add_inclusions([])
    assert tc.included_files == set()
    inclusions = ["tape"]
    tc.add_inclusions(inclusions)
    assert tc.included_files == {Path("assets/demo.tape").resolve()}


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
    count = tc.count_text_file(Path("assets/demo.gif"))
    assert count == 0
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
    count = tc.count_image_file(Path("assets/demo.tape"))
    assert count == 0
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


def test_tokencounter_filter_file(tmp_path):
    cfg = config.Config(
        Path("./tests/test_files"),
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

    inclusions = ["json"]
    tc.add_inclusions(inclusions)
    not_included = Path("output.json")
    inclusion_filtered = tc.filter_file(not_included)
    assert inclusion_filtered
    assert tc.ignored_files[".json"] == [not_included]
    tc.included_files = set()
    tc.ignored_files = dict()

    # TODO: figure out why this isn't getting flagged
    exclusions = ["html"]
    tc.add_exclusions(exclusions)
    excluded_file = Path("output.html")
    exclusion_filtered = tc.filter_file(excluded_file)
    assert exclusion_filtered
    assert tc.ignored_files[".html"] == [excluded_file]
    tc.excluded_files = set()
    tc.ignored_files = dict()

    # dotfiles
    dotfile = Path(".gitignore")
    dotfile_filtered = tc.filter_file(dotfile)
    assert dotfile_filtered
    assert [dotfile] in tc.ignored_files.values()
    tc.ignored_files = dict()

    # TODO: figure out why this isn't getting flagged
    # gitignore
    gitignored = tmp_path / "gitignored.json"
    gitignored.write_text('{"foo": "bar"}')
    gitignore_filtered = tc.filter_file(gitignored)
    assert gitignore_filtered
    assert tc.ignored_files[".json"] == [gitignored]
    tc.ignored_files = dict()

    # symlinks
    symlinked = Path("README.md")
    symlink_filtered = tc.filter_file(symlinked)
    assert symlink_filtered
    assert tc.ignored_files[".md"] == [symlinked]


def test_tokencounter_parse_file():
    cfg = config.Config(
        Path("tests/test_files"),
        True,
        False,
        False,
        False,
        True,
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
    image = Path("assets/contextwindow.png")
    extension, token_count = tc.parse_file(image)
    assert extension == ".png"
    assert token_count == 765


def test_tokencounter_parse_files():
    cfg = config.Config(
        Path("tests/test_files"),
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
    assert tc.ignored_files[".jpeg"] == [
        Path("tests/test_files/test_image.jpeg"),
    ]
    assert tc.ignored_files[""] == [
        Path("tests/test_files/.gitignore"),
        Path("tests/test_files/subtest/.invisible"),
    ]

    assert tc.scanned_files[".txt"].files == [
        {"file": Path("tests/test_files/testfile.txt").name, "tokens": 22},
    ]
    assert tc.total == 22


def test_tokencounter_grab_suffix(tmp_path):
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
    file = tmp_path / "foobar.tar.gz"
    file.write_text("hello mom")
    suffix = tc.grab_suffix(file)
    assert suffix == ".tar.gz"


# TODO: fix for github action
def test_tokencounter_txt_output(tmp_path):
    output_path = tmp_path / "foo.txt"
    with open(output_path, "w") as file:
        cfg = config.Config(
            Path("tests/test_files"),
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
    with open(output_path, "r") as file:
        output = file.read()
    assert "ignored:" in output
    assert "totals:" in output
    assert "tests/test_files/README.md" in output
    assert "tests/test_files/test_image.jpeg" in output
    assert "tests/test_files/.gitignore" in output
    assert "tests/test_files/subtest/.invisible" in output
    assert "grand total:" in output


# TODO: fix for github action
# This covers the TokenCounterEncoder too, technically - it only exists in output()
def test_tokencounter_json_output(tmp_path):
    output_path = tmp_path / "foo.json"
    with open(output_path, "w") as file:
        cfg = config.Config(
            Path("tests/test_files"),
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
    with open(output_path, "r") as file:
        payload = json.loads(file.read())
    assert payload["root"] == "tests/test_files"
    assert payload["total"] == 22
    assert set(payload["all_files"]) == {
        "README.md",
        "test_image.jpeg",
        ".gitignore",
        "testfile.txt",
        ".invisible",
    }
    assert set(payload["ignored_files"].keys()) == {".md", ".jpeg", ""}
    assert set(payload["ignored_files"][".md"]) == {"README.md"}
    assert set(payload["ignored_files"][".jpeg"]) == {"test_image.jpeg"}
    assert set(payload["ignored_files"][""]) == {".gitignore", ".invisible"}
    assert payload["scanned_files"][".txt"]["total"] == 22


# TODO: fix for github action
def test_tokencounter_html_output(tmp_path):
    output_path = tmp_path / "foo.html"
    with open(output_path, "w") as file:
        cfg = config.Config(
            Path("tests/test_files"),
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
    with open(output_path, "r") as file:
        output = file.read()
    assert "<table" in output
    assert "Scanned files in" in output
    assert "Ignored files in" in output
    assert "tests/test_files/README.md" in output
    assert "tests/test_files/test_image.jpeg" in output
    assert "tests/test_files/.gitignore" in output
    assert "tests/test_files/subtest/.invisible" in output


"""
    filecategory
"""


def test_filecategory():
    fc = models.FileCategory(".foo")
    assert fc.extension == ".foo"
    assert fc.files == []
    assert fc.total == 0
    assert fc.to_dict() == {"total": 0, "files": []}

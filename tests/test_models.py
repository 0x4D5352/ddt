from pathlib import Path
import string
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


def test_tokencounter_filter_file(base_config, tmp_path):
    # Create a test directory structure with .gitignore BEFORE creating Config
    test_root = tmp_path / "test_root"
    test_root.mkdir()

    # Create .gitignore file with patterns
    gitignore_path = test_root / ".gitignore"
    gitignore_path.write_text("gitignored.json\n")

    # Create the file that should be gitignored
    gitignored = test_root / "gitignored.json"
    gitignored.write_text('{"foo": "bar"}')

    # Now create the config - it will parse .gitignore during __post_init__
    cfg = base_config(root=test_root)
    tc = models.TokenCounter(cfg)

    # Test inclusions filter
    inclusions = ["json"]
    tc.add_inclusions(inclusions)
    not_included = Path("output.json")
    inclusion_filtered = tc.filter_file(not_included)
    assert inclusion_filtered
    assert tc.ignored_files[".json"] == [not_included]
    tc.included_files = set()
    tc.ignored_files = dict()

    # Test exclusions filter
    exclusions = ["html"]
    tc.add_exclusions(exclusions)
    excluded_file = Path("output.html")
    exclusion_filtered = tc.filter_file(excluded_file)
    assert exclusion_filtered
    assert tc.ignored_files[".html"] == [excluded_file]
    tc.excluded_files = set()
    tc.ignored_files = dict()

    # Test dotfiles filter
    dotfile = Path(".gitignore")
    dotfile_filtered = tc.filter_file(dotfile)
    assert dotfile_filtered
    assert [dotfile] in tc.ignored_files.values()
    tc.ignored_files = dict()

    # Test gitignore filter - the file was already created above
    gitignore_filtered = tc.filter_file(gitignored)
    assert gitignore_filtered
    assert tc.ignored_files[".json"] == [gitignored]
    tc.ignored_files = dict()

    # Test symlinks filter - README.md is outside test_root, so should be filtered
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


def test_tokencounter_grab_suffix(base_config, tmp_path):
    cfg = base_config(root=Path("assets"))
    tc = models.TokenCounter(cfg)
    file = Path("README.md")
    suffix = tc.grab_suffix(file)
    assert suffix == ".md"

    # Test multi-extension suffix with temporary file
    multi_ext_file = tmp_path / "foobar.tar.gz"
    multi_ext_file.write_text("hello mom")
    suffix = tc.grab_suffix(multi_ext_file)
    assert suffix == ".tar.gz"


def test_tokencounter_txt_output(base_config, test_directory, tmp_path):
    output_file = tmp_path / "foo.txt"

    with output_file.open("w") as file:
        cfg = base_config(
            root=test_directory,
            output=file,
            output_format="txt",
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()

    # Verify output file was created and contains expected structure
    actual = output_file.read_text()

    # Check for key elements in the output
    assert "ignored:" in actual
    assert "totals:" in actual
    assert ".txt tokens:" in actual
    assert "testfile.txt: 22 tokens" in actual
    assert ".txt total: 22 tokens" in actual
    assert "grand total: 22" in actual
    assert "remaining tokens given 128K context window: 127,978" in actual


# This covers the TokenCounterEncoder too, technically - it only exists in output()
def test_tokencounter_json_output(base_config, test_directory, tmp_path):
    import json

    output_file = tmp_path / "foo.json"

    with output_file.open("w") as file:
        cfg = base_config(
            root=test_directory,
            output=file,
            output_format="json",
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()

    # Verify JSON structure
    actual = json.loads(output_file.read_text())

    # Check for key structure elements
    assert "root" in actual
    assert "all_files" in actual
    assert "ignored_files" in actual
    assert "scanned_files" in actual
    assert "total" in actual

    # Verify specific values
    assert actual["total"] == 22
    assert ".txt" in actual["scanned_files"]
    assert actual["scanned_files"][".txt"]["total"] == 22
    assert len(actual["scanned_files"][".txt"]["files"]) == 1
    assert actual["scanned_files"][".txt"]["files"][0]["file"] == "testfile.txt"
    assert actual["scanned_files"][".txt"]["files"][0]["tokens"] == 22


def test_tokencounter_html_output(base_config, test_directory, tmp_path):
    output_file = tmp_path / "foo.html"

    with output_file.open("w") as file:
        cfg = base_config(
            root=test_directory,
            output=file,
            output_format="html",
        )
        tc = models.TokenCounter(cfg)
        tc.parse_files()
        tc.output()

    # Verify HTML structure
    actual = output_file.read_text()

    # Check for key HTML elements
    assert "<!DOCTYPE html>" in actual
    assert "<html" in actual
    assert "Scanned files in" in actual
    assert "<table>" in actual
    assert "</table>" in actual
    assert '<th scope="row">Grand Total</th>' in actual
    assert "testfile.txt" in actual
    assert "<td>22</td>" in actual


"""
    filecategory
"""


def test_filecategory():
    fc = models.FileCategory(".foo")
    assert fc.extension == ".foo"
    assert fc.files == []
    assert fc.total == 0
    assert fc.to_dict() == {"total": 0, "files": []}

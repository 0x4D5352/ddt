from pathlib import Path
import sys
from ddt import config, models
from ddt.tokenizer import Model

"""
    token counter
"""

def test_tokencounter_init():
    cfg = config.Config(Path('.'), False, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    assert tc.config == cfg
    assert tc.all_files == [file for file in Path('.').glob('**/*.*')]
    assert tc.ignored_files == dict()
    assert tc.scanned_files == dict()
    assert tc.excluded_files == set()
    assert tc.included_files == set()
    assert tc.total == 0

def test_tokencounter_to_dict():
    cfg = config.Config(Path('.'), False, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    result = tc.to_dict()
    assert result["root"] == str(Path('.'))
    assert result["all_files"] == [file.name for file in Path('.').glob('**/*.*')]
    assert result["ignored_files"] == dict()
    assert result["scanned_files"] == dict()
    assert result["total"] == 0

def test_tokencounter_to_text():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    result = tc._to_text()
    assert "=========================\n" in result
    assert "ignored:" in result
    assert "total:" in result

def test_tokencounter_to_html():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    result = tc._to_html()
    assert "<!DOCTYPE html>" in result
    assert "Scanned files in" in result
    assert "<table>" in result
    assert "</table>" in result
    assert '<th scope="row">Grand Total</th>' in result

def test_tokencounter_add_exclusions():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    exclusions = ["lock"]
    tc.add_exclusions(exclusions)
    assert tc.excluded_files == {Path("uv.lock").resolve()}

def test_tokencounter_add_inclusions():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    inclusions = ["lock"]
    tc.add_inclusions(inclusions)
    assert tc.included_files == {Path("uv.lock").resolve()}

def test_tokencounter_count_text_file():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    count = tc.count_text_file(Path("assets/demo.tape"))
    assert count == 830

# tokencounter count_image_file demo.gif: 1,105 tokens
def test_tokencounter_count_image_file():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    count = tc.count_image_file(Path("assets/demo.gif"))
    assert count == 1105

# tokencounter add_to_ignored

# tokencounter filter_file

# tokencounter parse_file

# tokencounter parse_files

# tokencounter grab_suffix

# tokencounter output

# TokenCounterEncoder custom instance


"""
    filecategory
"""

# Filecategory Init

# filecategory _to_dict


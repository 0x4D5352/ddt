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

# TokenCounter to_text
def test_tokencounter_to_text():
    cfg = config.Config(Path('.'), True, False, False, False, False, False, Model('gpt-4o'), sys.stdout," txt", [], [])
    tc = models.TokenCounter(cfg)
    result = tc._to_text()
    assert "=========================\n" in result
    assert "ignored:" in result
    assert "total:" in result

# tokencounter to_html

# tokencounter add_exclusions

# tokencounter add_inclusions

# tokencounter count_text_file

# tokencounter count_image_file

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


import pytest
from ddt import cli

def test_root_arg():
    parser = cli.setup_argparse()
    with pytest.raises(SystemExit):
        _ = parser.parse_args([])


def test_model_arg():
    parser = cli.setup_argparse()
    with pytest.raises(SystemExit):
        _ = parser.parse_args([".", "-m", "invalid_model"])

def test_output_arg():
    parser = cli.setup_argparse()
    with pytest.raises(SystemExit):
        _ = parser.parse_args([".", "-o", "src/"])

def test_output_type_args():
    parser = cli.setup_argparse()
    with pytest.raises(SystemExit):
        _ = parser.parse_args([".", "--json", "--html"])

def test_input_filter_args():
    parser = cli.setup_argparse()
    with pytest.raises(SystemExit):
        _ = parser.parse_args([".", "--include", ".py", "--exclude", ".json"])

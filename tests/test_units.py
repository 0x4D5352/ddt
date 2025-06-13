"""
    app.py
"""

# main function - basically integration/e2e testing???


"""
    parser.py
"""

# CLIParser Init

# CLIParser Args

# CLI positional - directory

# CLI optional - config file

# CLI optional - verbosity

# CLI optional - gitignore

# CLI optional - dotfiles

# cli optional - symlinks

# cli optional - images

# cli optional - resolve relative

# cli optional - model

# cli optional - output

# cli optional - output type - json

# cli optional - output type - html

# cli optional - filter group - inclusions

# cli optinoal - filter group - exclusions

# CLIParser Generate Config


"""
    models.py
"""

"""
    config and friends
"""

# Config Init

# Config Post Init

# Config Parse Gitignore


"""
    token counter and friends
"""

# TokenCounter Init

# TokenCounter to_dict

# TokenCounter to_text

# tokencounter to_html

# tokencounter add_exclusions

# tokencounter add_inclusions

# tokencounter count_text_file

# tokencounter count_image_file

# tokencounter parse_files

# tokencounter parse_files-add_to_ignored

# tokencounter grab_suffix

# tokencounter output

# tokenencoder custom instance

# Filecategory Init

# filecategory _to_dict


"""
    Tokenizer
"""

from ddt import tokenizer

# get_models


# TODO: update these two tests - they ONLY work for the default model of gpt-4o
def test_calclate_known_text_tokens():
    KNOWN_TEXT_TOKENS = [
        {"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "total":  22},
        {"text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.", "total":  41},
        {"text": "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Nunc accumsan semper libero quis vel nulla sagittis eget volutpat.", "total":  39},
        {"text": "Nulla facilisi. Sed sit amet nulla auctor, vestibulum magna sed, convallis ex. Fusce at purus ut orci gravida sodales.", "total":  29},
        {"text": "Nunc sed ante non metus lacinia finibus. Nam vel semper sapien, eu tempus libero. Aenean sit amet risus sit amet nisi fermentum iaculis.", "total":  35},
        {"text": "Cras ultricies ligula sed magna dictum porta. Morbi eget erat a est suscipit egestas. Etiam non lectus vel ex pulvinar dignissim.", "total":  30},
        {"text": "Nullam accumsan nibh ut arcu sodales, id luctus dolor facilisis. Pellentesque in neque et leo pharetra luctus sit amet at libero.", "total":  31},
    ]

    for case in KNOWN_TEXT_TOKENS:
        assert tokenizer.calculate_text_tokens(case["text"], 'gpt-4o') == case["total"]

def test_calculate_known_image_tokens():
    KNOWN_IMAGE_TOKENS = [
        {"width": 1024, "height": 1024, "total": 765},
        {"width": 2048, "height": 4096, "total": 1105},
    ]

    for case in KNOWN_IMAGE_TOKENS:
        assert tokenizer.calculate_image_tokens(case["width"],case["height"]) == case["total"]


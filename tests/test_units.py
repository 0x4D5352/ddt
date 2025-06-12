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

# get_models

# calculate_text_tokens

# calculate_image_tokens

# TODO:
# - Get values for the non-.tape files in assets
# - Pass image size to function
# - ALTERNATIVELY: dig into original docs and validate

def test_calculate_image_tokens():
    pass

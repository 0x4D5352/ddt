import tiktoken
from math import ceil


"""
Tokenizing methods
"""


def calculate_text_tokens(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string"""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Source for image token code: https://medium.com/@teekaifeng/gpt4o-visual-tokenizer-an-illustration-c69695dd4a39


def calculate_image_tokens(width: int, height: int) -> int:
    # Step 1: scale to fit within a 2048 x 2048 square (maintain aspect ratio)
    if width > 2048 or height > 2048:
        aspect_ratio = width / height
        if aspect_ratio > 1:
            width, height = 2048, int(2048 / aspect_ratio)
        else:
            width, height = int(2048 * aspect_ratio), 2048

    # Step 2: scale such that the shortest side of the image is 768px long
    if width >= height and height > 768:
        width, height = int((768 / height) * width), 768
    elif height > width and width > 768:
        width, height = 768, int((768 / width) * height)

    # Step 3: compute number of 512x512 tiles that can fit into the image
    tiles_width = ceil(width / 512)
    tiles_height = ceil(height / 512)

    # See https://platform.openai.com/docs/guides/vision/calculating-costs
    #   - 85 is the "base token" that will always be added
    #   - 1 tiles = 170 tokens
    total_tokens = 85 + 170 * (tiles_width * tiles_height)

    return total_tokens

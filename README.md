# DDT (Directory Diving Tokenizer)

![A GIF showing DDT running on the curl source code](./assets/demo.gif)

DDT is a CLI written in python (and rewritten in golang if i have time) that
will scan a directory and count the number of tokens per file, subdivided
by filetype. Useful for figuring out how difficult it will be for a Large
Language Model to hold the entirety of a given set of files in its context window.

## Installation and Use

To install DDT, clone this repo and choose the easy path or the hard path:

### The Easy Path

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), the
python package and project manager.
2. Run `uv run main.py /PATH/TO/TARGET`

### The Hard Path

1. Set up a python virtual environment with `python3 -m venv .venv`
2. Enter the virtual environment with `source .venv/bin/activate`
3. Run `python -m pip install -r pyproject.toml`
4. Run `python main.py /PATH/TO/TARGET`
5. Remember to run `exit` when you're done to leave the python venv!

### Command Line Flags

Beyond the traditional `-h` and `-v` flags, DDT can be configured a number of ways:

You can exclude filetypes by passing in one or more `-exclude FILETYPE` flags,
or you can include only specific filetypes with one or more `-include FILETYPE` flags.
You cannot specify both.

To save your output, pass the `-o` or `--output` flag followed by
a filename such as `out.json`. To save the file in a structured output,
pass one of the corresponding flags:

- `--json`
- `--html`

DDT ignores dotfiles (e.g. `.env` files and the `.git`
directory), respects the `.gitignore` file, discards symlinks, and does
not tokenize images. If you wish to alter any of these defaults, use the
provided options:

- `--include-dotfiles`
- `--include-gitignore`
- `--include-symlinks`
- `--include-images`

DDT works with both relative and absolute file paths. If you wish to force
the output to print absolute file paths, pass the `-r` or `--resolve-paths` flag.

The default tokenizer algorithm is based on GPT-4o. If you need to check the
token counts for older models, such as gpt-4 or text-davinci-003,
pass the corresponding model name into the `-m` or `--model` flag.
If the model you wish to test is not listed, reference the model list from
[this](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb) OpenAI Cookbook.

### Config File

If you wish to configure DDT without passing multiple command line flags, you
can provide a configuration file in JSON format with the `--config /path/to/config.json`
flag. Any value not specified within the config will use the default arguments.

## What are Tokens?

![A screenshot of OpenAI's Tokenizer page, showing the tokens of the Bee Movie script](./assets/beemovie.png)

Large Language Models, despite the name, do not understand language like you or I.
Instead, they understand an encoding (technically an embedding) of chunks of text
called tokens. A token can be a single letter like 'a', or it can be a word like
'the'. Some tokens include leading spaces (e.g. ' be'), to preserve sentence structure.
On average, a token works out to about 0.75 of an English word.

If you'd like to see examples of how text is broken up into tokens, check out
OpenAI's [Token Calculator](https://platform.openai.com/tokenizer) in their API
reference documentation.

Multimodal models have the ability to parse images as well as text. The
calculation is based on how many 512x512 tiles can fit into a scaled version
of the input image. To read more about how this process works, check out
[this article](https://medium.com/@teekaifeng/gpt4o-visual-tokenizer-an-illustration-c69695dd4a39)
by Tee Kai Feng.

## What is the Context Window?

![A toy example of parts of an LLM call in a context window](./assets/contextwindow.png)

For a Large Language Model, the context window represents "active knowlege" -
Information immediately relevant to the autocompletion algorithm LLMs use to
generate text. These tokens are what influences how the LLM uses the data it
has been trained on to predict the next token, which gets added to the context
and included in the next prediction. When the context window is full, the model
will begin behaving in unintended ways:

- The LLM might simply run out of tokens and stop generating text.
- The LLM might "forget" the oldest bit of information and behave strangely.
- The LLM might hallucinate information that no longer appears in the data.
- LLM Agents might lose functionality or send malformed input to its actions.

The current generation of LLMs (e.g. GPT-4o, GPT-o1, Claude Sonnet 3.5) have a
context window of 128,000 or 200,000 tokens. Future models are expected to have
between 500,000 and 1,000,000 tokens. The upper limit is currently unknown.

For reference: [curl](https://github.com/curl/curl) is approximately 1,750,000 tokens.

## Help Commands

```bash
usage: Tokenizer [-h] [-c CONFIG] [-v] [-g] [-d] [-s] [-i] [-r] [-m {gpt-4,gpt-4o,text-davinci-003}] [-o OUTPUT] [--json | --markdown | --html] [--exclude EXCLUDE | --include INCLUDE] directory

Crawls a given directory, counts the number of tokens per filetype in the project and returns a per-type total and grand total

positional arguments:
  directory             the relative or absolute path to the directory you wish to scan

options:
  -h, --help            show this help message and exit
  -c, --config CONFIG   Load one or more configurations from a file. Unset configs will use defaults.
  -v, --verbose         set to increase logging to console
  -g, --include-gitignore
                        include files and directories found in the .gitignore file
  -d, --include-dotfiles
                        include files and directories beginning with a dot (.)
  -s, --include-symlinks
                        include files and directories symlinked from outside the target directory
  -i, --include-images  include image files found within the directory
  -r, --resolve-paths   resolve relative file paths to their absolute location
  -m, --model {gpt-4,gpt-4o,text-davinci-003}
                        specify a model to use for token approximation. default is 'gpt-4o'
  -o, --output OUTPUT   redirect output from STDOUT to a file at the location specified.
  --json                save the results of the scan to a json file
  --markdown            save the results of the scan to a markdown file
  --html                save the results of the scan to a HTML file
  --exclude EXCLUDE     specify file formats to ignore from counting. this flag may be set multiple times for multiple entries. cannot be set if including files
  --include INCLUDE     specify file formats to include when counting. this flag may be set multiple times for multiple entries. cannot be set if excluding files

Made with <3 by 0x4D5352
```

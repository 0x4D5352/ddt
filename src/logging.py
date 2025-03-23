"""
Logging/Stdout Helpers
"""


def print_with_separator(string: str, sep: str = "-", after: bool = True) -> None:
    """
    A helper method to add line separators between sections of the stdout log.

    Args:
        string(string): the text to print.
        after(bool): If the text should print before or after the line separator. Defaults to after (True).
    """
    if not after:
        print(string)
    print("".join(sep for _ in range(50)))
    if after:
        print(string)


def print_if_verbose(string: str, is_verbose: bool) -> None:
    """
    A helper method that responds to the verbosity flag. is_verbose should always be set to the result of the is_verbose value in main()

    Args:
        string(string): the text to print.
        is_verbose(bool): If the text should print.
    """
    if not is_verbose:
        return
    print(string)

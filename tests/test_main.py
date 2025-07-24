import sys
from io import StringIO
from ddt import __main__


def test_stdin():
    og_stdin = sys.stdin
    mock_stdin = "Hello This Is A String Of Text"
    sys.stdin = StringIO(mock_stdin)
    __main__.main()
    print(sys.stdout)
    assert sys.stdout == 7
    sys.stdin = og_stdin

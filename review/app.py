"""TUI tool to visualize regular expressions in real time."""
import re
from sys import stdin

from blessed import Terminal
from lorem.text import TextLorem

RAW_LOREM = TextLorem(prange=(2, 2), psep="").text()
# WRAPPED_LOREM = re.sub(r"", r"\1\n", RAW_LOREM)


def echo(*args):
    """Print with no newline and flush immediately."""
    print(*args, end="", flush=True)


def main():
    """Fooling around."""
    term = Terminal()

    def _highlight_match(m):
        return term.bold(term.underline(m.group(0)))

    with term.fullscreen(), term.cbreak():
        while True:
            echo(term.move_y(term.height // 2))
            for line in term.wrap(RAW_LOREM, width=80):
                print(re.sub(r"(i[^it]+t)", _highlight_match, line))
            key = stdin.read(1)
            if key == "q":
                break


if __name__ == "__main__":
    main()

"""TUI tool to visualize regular expressions in real time."""
import re
from sys import argv, stdin

from blessed import Terminal
from lorem.text import TextLorem

RAW_LOREM = TextLorem(prange=(2, 2)).text()
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
            print(term.move(term.height // 2), 0)
            highlighted_lorem = re.sub(
                argv[1], _highlight_match, RAW_LOREM, flags=re.DOTALL
            )
            for line in term.wrap(highlighted_lorem, width=20):
                print(line)
            key = stdin.read(1)
            if key == "q":
                break


if __name__ == "__main__":
    main()

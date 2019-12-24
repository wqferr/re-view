"""TUI tool to visualize regular expressions in real time."""
import re
from sys import argv, stdin

from blessed import Terminal
from lorem.text import TextLorem

# RAW_LOREM = TextLorem(trange=(2, 3), prange=(2, 3), srange=(6, 6)).text()
RAW_LOREM = TextLorem().text()
# WRAPPED_LOREM = re.sub(r"", r"\1\n", RAW_LOREM)


def echo(*args):
    """Print with no newline and flush immediately."""
    print(*args, end="", flush=True)


def main():
    """Fooling around."""
    term = Terminal()
    margin = 2

    def _highlight_match(m):
        return term.bold(term.underline(m.group(0)))

    with term.fullscreen(), term.cbreak():
        key = None
        while True:
            echo(term.clear)
            echo(key)
            echo(term.move_y(term.height // 2))
            highlighted_lorem = re.sub(
                argv[1], _highlight_match, RAW_LOREM, flags=re.DOTALL
            )
            for line in term.wrap(highlighted_lorem, width=term.width - 2 * margin):
                echo(term.move_x(margin))
                print(line)
            key = stdin.read(1)
            if key == "q":
                break


if __name__ == "__main__":
    main()

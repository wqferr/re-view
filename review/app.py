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
        if len(argv) > 1:
            cur_regex = argv[1]
        else:
            cur_regex = ""

        while True:
            echo(term.clear)
            echo(term.move_y(term.height // 2))
            invalid_regex = False
            if cur_regex:
                try:
                    highlighted_lorem = re.sub(
                        cur_regex, _highlight_match, RAW_LOREM, flags=re.DOTALL
                    )
                    # highlighted_lorem = RAW_LOREM
                except:
                    invalid_regex = True
            else:
                invalid_regex = True

            if invalid_regex:
                highlighted_lorem = RAW_LOREM

            wrapped = term.wrap(highlighted_lorem, width=term.width - 2 * margin)
            echo(term.move_y((term.height - len(wrapped)) // 2))
            for line in wrapped:
                echo(term.move_x(margin))
                print(line)

            echo(term.move_y(term.height - 1))
            echo(cur_regex)
            key = term.inkey()
            if key.is_sequence:
                if key.name == "KEY_DELETE":
                    cur_regex = cur_regex[:-1]
            elif key.isascii:
                cur_regex = cur_regex + key
    print("GOT ", key, ord(key), key.is_sequence, str(key), key.name)


if __name__ == "__main__":
    main()

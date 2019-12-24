"""TUI tool to visualize regular expressions in real time."""
import re
from sys import argv

from blessed import Terminal
from lorem.text import TextLorem

RAW_LOREM = TextLorem().text()


def echo(*args):
    """Print with no newline and flush immediately."""
    print(*args, end="", flush=True)


def _get_highlighted_text(text, regex, highlight_function):
    if not regex:
        return text
    try:
        highlighted_text = re.sub(regex, highlight_function, text)
    except re.error:
        return text
    else:
        return highlighted_text


def _process_key(term, cur_regex):
    key = term.inkey()

    if key.is_sequence:
        if key.name == "KEY_DELETE":
            cur_regex = cur_regex[:-1]
    elif key.isascii:
        if key == "\x0c":
            print(term.clear)
        else:
            cur_regex = cur_regex + key
    return cur_regex


def main():
    """Fooling around."""
    term = Terminal()
    margin = 2

    def _highlight_match(m):
        return term.bold(term.underline(m.group(0)))

    if len(argv) > 1:
        cur_regex = argv[1]
    else:
        cur_regex = ""

    with term.fullscreen(), term.cbreak():
        while True:
            highlighted_lorem = _get_highlighted_text(
                RAW_LOREM, cur_regex, _highlight_match
            )

            wrapped = term.wrap(
                highlighted_lorem, width=term.width - 2 * margin, subsequent_indent="> "
            )
            echo(term.move_y((term.height - len(wrapped)) // 2))
            for line in wrapped:
                echo(term.move_x(margin))
                print(line)

            echo(term.move_y(term.height - 1))
            echo(cur_regex + term.clear_eol)

            try:
                cur_regex = _process_key(term, cur_regex)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()

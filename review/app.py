"""TUI tool to visualize regular expressions in real time."""
import re

from blessed import Terminal
from lorem.text import TextLorem

LOREM_GENERATOR = TextLorem()


def echo(*args):
    """Equivalent to print with no end and sep strings.

    Also flushes immediately.
    """
    print(*args, end="", sep="", flush=True)


class Application:
    """Fullscreen application."""

    def __init__(self, *, margin=2, initial_regex="", text=None):
        """See doc(Application)."""
        self.term = Terminal()
        self.margin = margin
        self.regex = initial_regex
        if text is None:
            self.text = LOREM_GENERATOR.text()
        else:
            self.text = text

    def _get_highlighted_text(self):
        if not self.regex:
            return self.text

        try:
            return re.sub(self.regex, self._highlight_match, self.text)
        except re.error:
            return self.text

    def _process_key(self):
        key = self.term.inkey()

        if key.is_sequence:
            if key.name == "KEY_DELETE":
                self.regex = self.regex[:-1]
        elif key.isascii:
            if key == "\x0c":
                echo(self.term.clear)
            else:
                self.regex = self.regex + key
        return self.regex

    def _highlight_match(self, m):
        matched_text = m.group(0)
        if not matched_text:
            return matched_text
        else:
            return self.term.bold_underline_reverse(matched_text)

    def _move(self, x=None, y=None):
        if x:
            echo(self.term.move_x(x))
        if y:
            echo(self.term.move_y(y))

    def _print_text(self):
        highlighted_text = self._get_highlighted_text()
        wrapped = self.term.wrap(
            highlighted_text,
            width=self.term.width - 2 * self.margin,
            subsequent_indent="> ",
        )
        self._move(y=(self.term.height - len(wrapped)) // 2)
        for line in wrapped:
            self._move(x=self.margin)
            echo(line + "\n")

    def _print_regex(self):
        self._move(y=self.term.height - 1)
        echo(self.regex + self.term.clear_eol)

    def run(self):
        """Start fullscreen application.

        Returns on KeyboardInterrupt.
        """
        # FIXME
        with self.term.fullscreen(), self.term.cbreak():
            while True:
                self._print_text()
                self._print_regex()

                try:
                    self._process_key()
                except KeyboardInterrupt:
                    break


def main():
    """Fooling around."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

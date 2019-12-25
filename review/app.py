"""TUI tool to visualize regular expressions in real time."""
import re
from argparse import ArgumentParser
from functools import reduce
from operator import or_ as bitwise_or

from blessed import Terminal
from lorem.text import TextLorem

LOREM_GENERATOR = TextLorem()
KEY_CLEAR_SCREEN = "\x0c"  # CTRL-M (enter/return)
KEY_FLAG_MODE = "\x06"  # CTRL-F
VALID_FLAGS = {"i", "m", "s", "u", "l", "x"}


def echo(*args):
    """Equivalent to print with no end and sep strings.

    Also flushes immediately.
    """
    print(*args, end="", sep="", flush=True)


def _get_flag(flag_letter):
    if flag_letter.lower() not in VALID_FLAGS:
        raise ValueError("Invalid flag: {flag_letter}")
    return getattr(re, flag_letter.upper())


class Application:
    """Fullscreen application."""

    def __init__(self, *, margin=2, initial_regex="", initial_flags=0, text=None):
        """See doc(Application)."""
        self.term = Terminal()
        self.margin = margin
        self.regex = initial_regex
        self.regex_cursor = len(self.regex)
        self.halt = False
        self.mode = "regex"
        self.flags = initial_flags
        self.last_flag_toggled = None
        if text is None:
            self.text = LOREM_GENERATOR.text()
        else:
            self.text = text

    def run(self):
        """Start fullscreen application.

        Returns on KeyboardInterrupt.
        """
        # FIXME
        with self.term.fullscreen(), self.term.cbreak():
            try:
                self._main_loop()
            except KeyboardInterrupt:
                pass
        print(self.term.width * "-")
        print(self.regex)
        print("Flags:", self.flags)

    def _get_highlighted_text(self):
        if not self.regex:
            return self.text

        try:
            return re.sub(self.regex, self._highlight_match, self.text, flags=self.flags)
        except re.error:
            return self.text
        except ValueError:
            # Invalid flag
            if self.last_flag_toggled is not None:
                self._toggle_flag(self.last_flag_toggled)
                self.last_flag_toggled = None
                return self._get_highlighted_text()
            else:
                raise

    def _move_regex_cursor(self, delta):
        self.regex_cursor += delta
        self.regex_cursor = max(0, min(len(self.regex), self.regex_cursor))

    def _add_char(self, char):
        regex_start = self.regex[: self.regex_cursor]
        regex_end = self.regex[self.regex_cursor :]
        self.regex = regex_start + char + regex_end
        self._move_regex_cursor(+1)

    def _erase_char(self):
        if self.regex_cursor == 0:
            # Cursor at start, do nothing
            return

        new_start = self.regex[: self.regex_cursor - 1]
        new_end = self.regex[(self.regex_cursor) :]

        self.regex = new_start + new_end
        self._move_regex_cursor(-1)

    def _process_key(self):
        key = self.term.inkey()

        if self.mode == "regex":
            self._process_key_regex_mode(key)
        else:
            self._process_key_flag_mode(key)

    def _process_key_regex_mode(self, key):
        if key.is_sequence:
            self._process_sequence_key(key)
        elif key.isascii:
            self._process_typed_key(key)

    def _process_key_flag_mode(self, key):
        if key.is_sequence and key.name == "KEY_ESCAPE":
            self._exit_flag_mode()

        key = key.lower()
        try:
            self._toggle_flag(key)
        except ValueError:
            pass
        finally:
            self._exit_flag_mode()

    def _process_sequence_key(self, sequence):
        if sequence.name == "KEY_DELETE":
            self._erase_char()
        elif sequence.name == "KEY_LEFT":
            self._move_regex_cursor(-1)
        elif sequence.name == "KEY_RIGHT":
            self._move_regex_cursor(+1)
        elif sequence.name == "KEY_ENTER":
            self.halt = True
        elif sequence.name == "KEY_FIND":
            self.regex_cursor = 0
        elif sequence.name == "KEY_SELECT":
            self.regex_cursor = len(self.regex)

    def _process_typed_key(self, key):
        if key == KEY_CLEAR_SCREEN:
            echo(self.term.clear)
        elif key == KEY_FLAG_MODE:
            self.mode = "flag"
        elif key.isprintable():
            self._add_char(str(key))

    def _highlight_match(self, m):
        matched_text = m.group(0)
        if not matched_text:
            return matched_text
        else:
            return self.term.bold_underline_reverse(matched_text)

    def _move(self, x=None, y=None):
        if x is not None:
            echo(self.term.move_x(x))
        if y is not None:
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
        echo(self.term.normal)

    def _print_prompt(self):
        if self.mode == "flag":
            self._print_flags()
        else:
            self._print_regex()

    def _print_regex(self):
        self._move(y=self.term.height - 1)
        echo(self.regex + self.term.clear_eol)
        self._move(x=self.regex_cursor)

    def _print_flags(self):
        self._move(x=0, y=self.term.height - 3)
        print("[FLAG]")
        print(f"Press any of {''.join(VALID_FLAGS)} to toggle flags, or ESC to cancel")
        current_flag_letters = [
            letter
            for letter in VALID_FLAGS
            if self.flags & getattr(re, letter.upper()) > 0
        ]
        echo(
            f"Current flags: {''.join(current_flag_letters) or None}",
            self.term.clear_eol,
        )

    def _cleanup_flag_prompt(self):
        echo(self.term.clear)
        # self._move(x=0, y=self.term.height - 3)
        # print((self.term.clear_eol + "\n") * 3)

    def _main_loop(self):
        while not self.halt:
            self._print_text()
            self._print_prompt()
            self._process_key()

    def _toggle_flag(self, flag_letter):
        self.flags ^= _get_flag(flag_letter)
        self.last_flag_toggled = flag_letter

    def _exit_flag_mode(self):
        self.mode = "regex"
        self._cleanup_flag_prompt()


def _read_file(filename):
    try:
        with open(filename, "rt") as file:
            return file.read()
    except FileNotFoundError:
        return None


def main():
    """Fooling around."""
    parser = ArgumentParser()
    parser.add_argument(
        "--regex", "-r", dest="initial_regex", help="initial regex", default="",
    )
    parser.add_argument(
        "--flags", "-f", dest="initial_flags", help="initial regex flags", default=""
    )
    parser.add_argument(
        "text_file",
        type=str,
        help="text file to use as test cases",
        nargs="?",
        default="",
    )
    args = parser.parse_args()

    initial_flags = reduce(bitwise_or, map(_get_flag, args.initial_flags), 0)
    app = Application(
        initial_regex=args.initial_regex,
        initial_flags=initial_flags,
        text=_read_file(args.text_file),
    )
    app.run()


if __name__ == "__main__":
    main()

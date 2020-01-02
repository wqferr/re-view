"""TUI tool to visualize regular expressions in real time.

Command line usage:
    review [options] [--] [INPUT_FILE | -]

    --help, -h                      show this help message
    --regex REGEX, -r REGEX         set starting regex
    --flags [FLAGS], -f [FLAGS]     set starting flags
        If -f or --flags is passed with no arguments, start program with no active
        flags.

    INPUT_FILE is the file to be read and displayed to test the regex.
    If - (a single dash) is supplied instead of a filename, the text is
    read from stdin.
    If INPUT_FILE is not supplied at all, a randomly generated Lorem-style text
    will be used.

Python regex reference:
    https://docs.python.org/3/library/re.html

Application usage:
    The window is divided into two parts:
    The lower half displays the current regular expression (regex) being tested.
    The upper half displays text that is highlighted according to the regex typed.

    The text displayed in the upper part may be wrapped.
    Continuation of long lines start with ">", and do not match ^, even if the
    multiline flag is enabled.
    If the input text is too large to fit on screen, you may use the up and down
    arrows to scroll the text.

    If there is a rendering issue, CTRL-L will force a redraw.

    You may edit the regex by typing on your keyboard.
    The arrows, home and end keys move the cursor to edit different
    parts of the regex.
    The backspace and delete keys both erase the character before the cursor.

    To change the active regex flags, press CTRL-F to enter "flag mode".
    While in flag mode, the currently active flags are displayed, and you may
    press any of the given keys to activate or deactivate the corresponding
    flag.

    If you enable a flag that is incompatible with any others, these others
    will be disabled and the new one will take place.

    To exit the application, send SIGTERM (CTRL-C) to the
    process. It will write the regex and its flags to stdout.
"""
import re
from argparse import ArgumentParser
from functools import reduce
from operator import or_ as bitwise_or
from sys import stdin

from blessed import Terminal
from lorem.text import TextLorem

from review import __version__

LOREM_GENERATOR = TextLorem()
KEY_CLEAR_SCREEN = "\x0c"  # CTRL-M (enter/return)
KEY_FLAG_MODE = "\x06"  # CTRL-F
VALID_FLAGS = {"I", "M", "S", "U", "A", "X"}


def echo(*args):
    """Equivalent to print with no end and sep strings.

    Also flushes immediately.
    """
    print(*args, end="", sep="", flush=True)


def _get_flag(flag_letter):
    flag_letter = flag_letter.upper()
    if flag_letter not in VALID_FLAGS:
        raise ValueError("Invalid flag: {flag_letter}")
    return getattr(re, flag_letter)


class Application:
    """Fullscreen application."""

    def __init__(self, *, initial_regex="", initial_flags=0, text=None):
        """See doc(Application)."""
        self.term = Terminal()
        self.regex = initial_regex
        self.regex_cursor = len(self.regex)
        self.start_line = 0
        self.mode = "regex"
        self.show_ctrl_f_prompt = True
        self.flags = initial_flags
        self.error_msg = ""
        if text is None:
            self.text = LOREM_GENERATOR.text()
        else:
            self.text = text
        self.lines = self.text.split("\n")

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
        print(self.regex)
        print("Flags:", self._get_active_flags_str())

    def _highlight(self, text):
        return self.term.bold_underline_reverse(text)

    def _get_highlighted_text(self):
        self.error_msg = ""
        if not self.regex:
            return self.text

        try:
            return re.sub(self.regex, self._highlight_match, self.text, flags=self.flags)
        except re.error as err:
            self.error_msg = err.msg
            return self.text

    def _highlight_line(self, line):
        self.error_msg = ""
        if not self.regex:
            return line
        try:
            return re.sub(self.regex, self._highlight_match, line, flags=self.flags)
        except re.error as err:
            self.error_msg = err.msg
            return line

    def _move_regex_cursor(self, delta):
        self.regex_cursor += delta
        self.regex_cursor = max(0, min(len(self.regex), self.regex_cursor))

    def _scroll_screen(self, delta):
        self.start_line += delta
        self.start_line = max(0, min(len(self.lines) - self.term.height, self.start_line))

    def _add_char(self, char):
        regex_start = self.regex[: self.regex_cursor]
        regex_end = self.regex[self.regex_cursor :]
        self.regex = regex_start + char + regex_end
        self._move_regex_cursor(+1)

    def _erase_char_behind(self):
        if self.regex_cursor == 0:
            # Cursor at start, do nothing
            return

        new_start = self.regex[: self.regex_cursor - 1]
        new_end = self.regex[self.regex_cursor :]

        self.regex = new_start + new_end
        self._move_regex_cursor(-1)

    def _erase_char_in_front(self):
        if self.regex_cursor == len(self.regex):
            # Cursor at end, do nothing
            return

        new_start = self.regex[: self.regex_cursor]
        new_end = self.regex[self.regex_cursor + 1 :]
        self.regex = new_start + new_end

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
        if sequence.name in ("KEY_DELETE", "KEY_BACKSPACE"):
            # TERMINALS DON'T KNOW HOW TO SEND KEY SIGNALS WTF
            if ord(sequence[-1]) == 127:  # Actually backspace
                self._erase_char_behind()
            else:  # Actually delete
                self._erase_char_in_front()
        elif sequence.name == "KEY_LEFT":
            self._move_regex_cursor(-1)
        elif sequence.name == "KEY_RIGHT":
            self._move_regex_cursor(+1)
        elif sequence.name == "KEY_UP":
            self._scroll_screen(-1)
        elif sequence.name == "KEY_DOWN":
            self._scroll_screen(+1)
        elif sequence.name == "KEY_FIND":
            self.regex_cursor = 0
        elif sequence.name == "KEY_SELECT":
            self.regex_cursor = len(self.regex)

    def _process_typed_key(self, key):
        if key == KEY_CLEAR_SCREEN:
            echo(self.term.clear)
        elif key == KEY_FLAG_MODE:
            self._enter_flag_mode()
        elif key.isprintable():
            self._add_char(str(key))

    def _highlight_match(self, m):
        matched_text = m.group(0)
        if not matched_text:
            return matched_text
        else:
            highlighted_chars = (
                self.term.bold_underline_reverse(c) for c in matched_text
            )
            return "".join(highlighted_chars)

    def _move(self, x=None, y=None):
        if x is not None:
            echo(self.term.move_x(x))
        if y is not None:
            echo(self.term.move_y(y))

    def _print_text(self):
        lines_on_screen = 0
        line_buffer = []
        for line in self.lines[self.start_line :]:
            line = self._highlight_line(line)
            wrapped_line = self.term.wrap(
                line,
                width=self.term.width,
                subsequent_indent=self.term.bright_black(">"),
            )
            for wrap in wrapped_line:
                real_line = wrap + self.term.clear_eol + self.term.normal
                line_buffer.append(real_line)
                lines_on_screen += 1
            if lines_on_screen > self.num_text_display_lines:
                break
        self._move(x=0, y=0)
        echo("\n".join(line_buffer))

    @property
    def num_text_display_lines(self):
        """Get number of lines available to show highlighted text."""
        return self.term.height - 3

    def _print_prompt(self):
        if self.mode == "flag":
            self._print_flags()
        else:
            self._print_regex()

    def _print_regex(self):
        self._move(x=0, y=self.num_text_display_lines + 1)
        echo(
            self.term.black_on_red(self.error_msg), self.term.clear_eol, "\n",
        )
        echo(self.regex)
        echo("  ", self.term.bright_black(self._get_active_flags_str()))
        if self.show_ctrl_f_prompt:
            echo(self.term.bright_black(" (press CTRL-F to edit flags)"))
        echo(self.term.clear_eol)
        self._move(x=self.regex_cursor)

    def _print_flags(self):
        self._move(x=0, y=self.term.height - 3)
        echo("[FLAG]", self.term.clear_eol, "\n")
        echo(
            f"Press any of {''.join(VALID_FLAGS)} to toggle flags, or ESC to cancel",
            self.term.clear_eol,
            "\n",
        )
        echo(
            f"Current flags: {self._get_active_flags_str()}", self.term.clear_eol,
        )

    def _get_active_flags_str(self):
        current_flag_letters = [
            letter for letter in VALID_FLAGS if self.flags & getattr(re, letter) > 0
        ]
        return "".join(current_flag_letters) or "no flags"

    def _cleanup_flag_prompt(self):
        echo(self.term.clear)

    def _main_loop(self):
        while True:
            self._print_text()
            self._print_prompt()
            self._process_key()

    def _toggle_flag(self, flag_letter):
        if flag_letter.upper() == "U":
            self._disable_flag("A")
        elif flag_letter.upper() == "A":
            self._disable_flag("U")
        self.flags ^= _get_flag(flag_letter)

    def _disable_flag(self, flag_letter):
        self.flags &= ~_get_flag(flag_letter)

    def _enter_flag_mode(self):
        self.mode = "flag"
        self.show_ctrl_f_prompt = False

    def _exit_flag_mode(self):
        self.mode = "regex"
        self._cleanup_flag_prompt()


def _read_text(filename):
    if filename == "-":
        return stdin.read()
    try:
        with open(filename, "rt") as file:
            return file.read()
    except FileNotFoundError:
        return None


def main():
    """Fooling around."""
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--regex", "-r", dest="initial_regex", default="",
    )
    parser.add_argument("--flags", "-f", dest="initial_flags", default="", nargs="?")
    parser.add_argument(
        "text_file", type=str, nargs="?", default="",
    )
    parser.add_argument("--version", "-v", dest="show_version", action="store_true")
    parser.add_argument("--help", "-h", dest="show_help", action="store_true")
    args = parser.parse_args()
    if args.show_help:
        print(__doc__)
        return
    if args.show_version:
        print("RE-view version", __version__)
        return

    initial_flags = args.initial_flags or ""
    initial_flags = reduce(bitwise_or, map(_get_flag, initial_flags), 0)
    app = Application(
        initial_regex=args.initial_regex,
        initial_flags=initial_flags,
        text=_read_text(args.text_file),
    )
    app.run()


if __name__ == "__main__":
    main()

RE-view
-------
TUI tool to visualize regular expressions in real time.

Command line usage
------------------
```
review [options] [--] [INPUT_FILE | -]

--help, -h                      show this help message
--regex REGEX, -r REGEX         set starting regex
--flags [FLAGS], -f [FLAGS]     set starting flags, defaults to M
    If -f or --flags is passed with no arguments, start program with no active
    flags.

`INPUT_FILE` is the file to be read and displayed to test the regex.
If - (a single dash) is supplied instead of a filename, the text is
read from stdin.
If `INPUT_FILE` is not supplied at all, a randomly generated Lorem-style text
will be used.
```

Screenshots
-----------
Coming `Soon`™.

Python regex reference
----------------------
https://docs.python.org/3/library/re.html

Application usage
-----------------
The window is divided into two parts:
- The lower half displays the current regular expression (regex) being tested.
- The upper half displays text that is highlighted according to the regex typed.

The text displayed in the upper part may be wrapped.
Continuation of long lines start with "> ", and do not match `^`, even if the
multiline flag is enabled.

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


RE-view
=======
TUI tool to visualize regular expressions in real time.

Screenshots
-----------

### Simple usage
Below is a screenshot of a common use case: you have a file with sample text you want
to validate a regex on, and the application shows you where the typed regex will match.

This example matches all words that begin with any of `a`, `e`, `i`, `o` or `u`.
Note that it only considers lowercase vowels for this.

![Usage example](https://raw.githubusercontent.com/wqferr/re-view/master/.assets/basic.png)

### Regex flags
You can set or unset any of the flags of the python `re` module, like multiline.
In this and the following examples, the dim uppercase `I` indicates that
the case-insensitive flag is active.

This example matches all words that begin with a vowel, be it upper or lowercase.

![Regex flags in action](https://raw.githubusercontent.com/wqferr/re-view/master/.assets/flags.png)

### Captures
You can capture specific parts of the match, and the application will highlight the
appropriate portion of the text.

For now, only non-named capture groups are available, and only limited to 4 groups
(not considering group 0, the whole match). Also, for now it is not possible to customize
colors, but it is a planned feature for you colorblind folk. I tried to select a palette
that's both (mostly) readable and also compatible with terminals with 16 colors.

Turns out, that's pretty hard! I prioritized the terminal compatibility for now. If you
wish to skip a group, simply add an empty capture (i.e., `()`) somewhere in the regex. Also, colors
are grouped in such a way that ones that are similar (as far as I know) have different
statuses of underline or bold, so that's another way to differentiate them.

Groups are highlighted as follows:
- 0: (Any non-captured part of match) underlined black-on-white
- 1: Underlined black-on-blue
- 2: Underlined black-on-yellow
- 3: Bold black-on-green
- 4: Bold black-on-red

![Capture groups](https://raw.githubusercontent.com/wqferr/re-view/colored-captures/.assets/captures.png)

### Errors
If there's an error in the regex, it will warn you in bright red.

This example shows that no highlights are shown, and a bright red message describing
the error is shown above the regex.

![An example of a lookahead](https://raw.githubusercontent.com/wqferr/re-view/master/.assets/error.png)

### Lookahead
It also accepts lookaheads! In fact, it accepts any feature the `re` module accepts.
If you don't know what a lookahead (or lookbehind is), don't worry, this is just
and example of what it *can* do.

This examples matches only words that begin with a vowel (upper or lowercase)
and that precedes either `.`, `?` or `!`.

![An example of a lookahead](https://raw.githubusercontent.com/wqferr/re-view/master/.assets/lookahead.png)

### When you're done editing
Send `SIGTERM` (`CTRL-C`) to stop the application. It will print out the resulting regex
and flags that were active.

This example shows what would happen if you sent `SIGTERM` to the application in the state
shown by the "Lookahead" example.

![A look at stdout](https://raw.githubusercontent.com/wqferr/re-view/master/.assets/stdout.png)

Command line usage
------------------
```
review [options] [--] [INPUT_FILE | -]

--help, -h                      show this help message
--regex REGEX, -r REGEX         set starting regex
--flags [FLAGS], -f [FLAGS]     set starting flags, defaults to no flags
    If -f or --flags is passed with no arguments, start program with no active
    flags.

`INPUT_FILE` is the file to be read and displayed to test the regex.
If - (a single dash) is supplied instead of a filename, the text is
read from stdin.
If `INPUT_FILE` is not supplied at all, a randomly generated Lorem-style text
will be used.
```

Application usage
-----------------
The window is divided into two parts:
- The lower half displays the current regular expression (regex) being tested.
- The upper half displays text that is highlighted according to the regex typed.

The text displayed in the upper part may be wrapped.
Continuation of long lines start with ">", and do not match `^`, even if the
multiline flag is enabled.
If the input text is too large to fit on screen, you may use the up and down
arrows to scroll the text.

If there is a rendering issue, `CTRL-L` will force a redraw.

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

To exit the application, send `SIGTERM` (`CTRL-C`) to the
process. It will write the regex and its flags to stdout.

Python regex reference
----------------------
https://docs.python.org/3/library/re.html

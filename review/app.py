from blessed import Terminal


def main():
    """Execute tests."""
    term = Terminal()
    print(term.bold("hello!"))
    print(term.bold(term.underline("HELLO")))


if __name__ == "__main__":
    main()

import os
import sys

def can_use_colors():
    # Respect standard NO_COLOR env var
    if os.environ.get("NO_COLOR") is not None:
        return False
    # Check if output is a TTY
    if not sys.stdout.isatty():
        return False
    # Check if TERM is dumb
    if os.environ.get("TERM") == "dumb":
        return False
    return True

_COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "reset": "\033[0m"
}

def colorize(text, color_name):
    if not can_use_colors() or color_name not in _COLORS:
        return text
    return f"{_COLORS[color_name]}{text}{_COLORS['reset']}"

def red(text):
    return colorize(text, "red")

def green(text):
    return colorize(text, "green")

def yellow(text):
    return colorize(text, "yellow")

def blue(text):
    return colorize(text, "blue")

def cyan(text):
    return colorize(text, "cyan")

def bold(text):
    return colorize(text, "bold")

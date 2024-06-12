import sys


def info(message: str):
    print(message)


def error(message: str):
    print(f"ERROR: {message}")
    sys.exit(1)

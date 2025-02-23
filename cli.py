from cli.commands import execute_extraction
from cli.parser import parse_args
from cli.ui import display_error
import sys


if __name__ == "__main__":
    args = sys.argv[1:]

    try:
        parsed_args = parse_args(args)
        execute_extraction(parsed_args)
    except Exception as e:
        display_error(e)

import argparse

from .create import get_data_create_parser, execute_data_create_tool
from .inspect import get_data_inspect_parser, execute_data_inspect_tool
from .lint import get_data_lint_parser, execute_data_lint_tool

TOOLS = {
    'create': execute_data_create_tool,
    'inspect': execute_data_inspect_tool,
    'lint': execute_data_lint_tool
}

def get_data_parser():
    parser = argparse.ArgumentParser(description='Surround Data Container Tool')
    sub_parser = parser.add_subparsers(description='This tool must be called with one of the following commands', dest='command')

    sub_parser.add_parser('create', parents=[get_data_create_parser()], help='Capture new data into a container with metadata', description='Create a data container from a file or directory')
    sub_parser.add_parser('inspect', parents=[get_data_inspect_parser()], help='Inspect a data containers contents and/or metadata', description='Inspect the metadata and/or contents of a data container')
    sub_parser.add_parser('lint', parents=[get_data_lint_parser()], help='Check the validity of a data container', description='Check the validity of a data container')

    return parser

def execute_data_tool(parser, args):
    if args.command in TOOLS:
        TOOLS[args.command](parser, args)
    elif not args.command:
        parser.print_help()
    else:
        parser.print_usage()

def main():
    parser = get_data_parser()
    args = parser.parse_args()

    execute_data_tool(parser, args)

if __name__ == "__main__":
    main()

import argparse

from .create import get_data_create_parser, execute_data_create_tool
from .inspect import get_data_inspect_parser, execute_data_inspect_tool
from .lint import get_data_lint_parser, execute_data_lint_tool

# Dictionary of functions which execute their respective tool
TOOLS = {
    'create': execute_data_create_tool,
    'inspect': execute_data_inspect_tool,
    'lint': execute_data_lint_tool
}

def get_data_parser():
    """
    Generates the parser used for the data container tool.

    :returns: the parser generated
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(description='Surround Data Container Tool')
    sub_parser = parser.add_subparsers(description='This tool must be called with one of the following commands', dest='command')

    sub_parser.add_parser('create', parents=[get_data_create_parser()], help='Capture new data into a container with metadata', description='Create a data container from a file or directory')
    sub_parser.add_parser('inspect', parents=[get_data_inspect_parser()], help='Inspect a data containers contents and/or metadata', description='Inspect the metadata and/or contents of a data container')
    sub_parser.add_parser('lint', parents=[get_data_lint_parser()], help='Check the validity of a data container', description='Check the validity of a data container')

    return parser

def execute_data_tool(parser, args, extra_args):
    """
    Executes the data container tool using the parser and arguments provided.

    Uses the TOOLS dictionary and the command argument to execute the correct
    sub-command function.

    :param parser: the parser used to get the arguments
    :type parser: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    if args.command in TOOLS:
        TOOLS[args.command](parser, args)
    elif not args.command:
        parser.print_help()
    else:
        parser.print_usage()

def main():
    """
    Entry point used when this script is executed directly, parses the arguments and executes
    the data container tool.
    """

    parser = get_data_parser()
    args = parser.parse_args()

    execute_data_tool(parser, args, [])

if __name__ == "__main__":
    main()

import argparse
import sys
import logging

from .remote import cli as remote_cli
from .project import cli as project_cli

def parse_tool_args(parsed_args, remote_parser, tool):
    if tool == "tutorial":
        project_cli.parse_tutorial_args(parsed_args)
    elif tool == "lint":
        project_cli.parse_lint_args(parsed_args)
    elif tool == "run":
        project_cli.parse_run_args(parsed_args)
    elif tool == "remote":
        remote_cli.parse_remote_args(remote_parser, parsed_args)
    elif tool == "add":
        remote_cli.parse_add_args(parsed_args)
    elif tool == "pull":
        remote_cli.parse_pull_args(parsed_args)
    elif tool == "push":
        remote_cli.parse_push_args(parsed_args)
    elif tool == "list":
        remote_cli.parse_list_args(parsed_args)
    else:
        project_cli.parse_init_args(parsed_args)

def main():
    logging.disable(logging.CRITICAL)

    parser = argparse.ArgumentParser(prog='surround', description="The Surround Command Line Interface")
    sub_parser = parser.add_subparsers(description="Surround must be called with one of the following commands")

    project_cli.add_tutorial_parser(parser, sub_parser)
    project_cli.add_init_parser(parser, sub_parser)
    project_cli.add_run_parser(parser, sub_parser)

    remote_parser = remote_cli.add_remote_parser(sub_parser)
    remote_cli.create_add_parser(sub_parser)
    remote_cli.add_pull_parser(sub_parser)
    remote_cli.add_push_parser(sub_parser)
    remote_cli.add_list_parser(sub_parser)

    # Check for valid sub commands as 'add_subparsers' in Python < 3.7
    # is missing the 'required' keyword
    tools = ["init", "tutorial", "lint", "run", "remote", "add", "pull", "push", "list"]
    try:
        if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
            parser.print_help()
        elif len(sys.argv) < 2 or not sys.argv[1] in tools:
            print("Invalid subcommand, must be one of %s" % tools)
            parser.print_help()
        else:
            tool = sys.argv[1]
            parsed_args = parser.parse_args()
            parse_tool_args(parsed_args, remote_parser, tool)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")

if __name__ == "__main__":
    main()

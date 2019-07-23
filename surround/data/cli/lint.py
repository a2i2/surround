import argparse

def get_data_lint_parser():
    parser = argparse.ArgumentParser(description='Check the validity of a data container', add_help=False)
    return parser

def execute_data_lint_tool(parser, args):
    print("Running lint tool..")

def main():
    parser = get_data_lint_parser()
    args = parser.parse_args()

    execute_data_lint_tool(parser, args)

if __name__ == "__main__":
    main()

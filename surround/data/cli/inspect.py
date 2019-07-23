import argparse

def get_data_inspect_parser():
    parser = argparse.ArgumentParser(description='Inspect the metadata and/or contents of a data container', add_help=False)
    return parser

def execute_data_inspect_tool(parser, args):
    print("Running inspect tool..")

def main():
    parser = get_data_inspect_parser()
    args = parser.parse_args()

    execute_data_inspect_tool(parser, args)

if __name__ == "__main__":
    main()

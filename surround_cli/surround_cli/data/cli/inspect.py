import os
import argparse

from ..container import DataContainer


def is_valid_file(parser, x):
    """
    Checks argument from parser is a valid container file path (*.data.zip)

    :param parser: the parser
    :type parser: :class:`argparse.ArgumentParser`
    :param x: the value being checked
    :type x: str
    :returns: the value if valid, false otherwise
    :rtype: str or bool
    """

    if not os.path.exists(x):
        parser.error("Failed to locate the container specified")
        return False

    if not os.path.isfile(x):
        parser.error("The path specified must be a file")
        return False

    splitext = os.path.splitext(x)
    if ".data" not in splitext[0] or splitext[1] != ".zip":
        parser.error("The file must have the extension .data.zip!")
        return False

    return x


def get_data_inspect_parser():
    """
    Generates the parser for the inspector sub-command of the data container CLI tool.

    :returns: the parser generated
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(
        description="Inspect the metadata and/or contents of a data container",
        add_help=False,
    )

    parser.add_argument(
        "container_file",
        type=lambda x: is_valid_file(parser, x),
        help="Path to the data container to inspect",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-m",
        "--metadata-only",
        action="store_true",
        help="Inspect the metadata of the container only",
    )
    group.add_argument(
        "-c",
        "--content-only",
        action="store_true",
        help="Inspect the contents of the container only",
    )

    return parser


def perform_metadata_inspection(container):
    """
    Prints the metadata of the container to the terminal.

    :param container: the container
    :type container: :class:`surround.data.container.DataContainer`
    """

    metadata = container.metadata
    print("Metadata format version: %s" % metadata["version"])
    print("Summary Metadata:")
    print("  Title:          %s" % metadata["summary"]["title"])
    print("  Description:    %s" % metadata["summary"]["description"])
    print("  Creator:        %s" % metadata["summary"]["creator"])
    print("  Date:           %s" % metadata["summary"]["date"])
    print("  Publisher:      %s" % metadata["summary"]["publisher"])
    print("  Contributor:    %s" % metadata["summary"]["contributor"])
    print("  Subject:        %s" % metadata["summary"]["subject"])
    print("  Formats:        %s" % metadata["summary"]["formats"])
    print("  Types:          %s" % metadata["summary"]["types"])
    print("  Identifier:     %s" % metadata["summary"]["identifier"])
    print("  Rights:         %s" % metadata["summary"]["rights"])
    print("  Under Ethics:   %s" % metadata["summary"]["under-ethics"])
    print("  Language:       %s\n" % metadata["summary"]["language"])

    if metadata.get_property("manifests"):
        for manifest in metadata["manifests"]:
            print("'%s' Group Metadata:" % manifest["path"])
            print("  Description:   %s" % manifest["description"])
            print("  Language:      %s" % manifest["language"])
            print("  Formats:       %s" % manifest["formats"])
            print("  Types:         %s\n" % manifest["types"])


def perform_content_inspection(container):
    """
    Prints the files inside the container to the terminal.

    :param container: the container
    :type container: :class:`surround.data.container.DataContainer`
    """

    print("Contents:")
    for content in container.get_files():
        print(content)


def execute_data_inspect_tool(parser, args):
    """
    Executes the inspect sub-command of the data container CLI tool.
    Which allows the inspection of a data container, showing metadata
    and/or files in the container.

    :param parser: parser used to parse the arguments
    :type parser: :class:`argparse.ArgumentParser`
    :param args: the arguments supplied the user
    :type args: :class:`argparse.Namespace`
    """

    print("=========[Inspecting data container]============")
    print("Opening data container: %s\n" % args.container_file)

    try:
        container = DataContainer(args.container_file)
    except Exception:
        print("error: failed to open the container: %s" % args.container_file)
        return

    if not args.content_only:
        perform_metadata_inspection(container)

    if not args.metadata_only:
        perform_content_inspection(container)


def main():
    """
    Entry point used when this script is executed directly.
    """

    parser = get_data_inspect_parser()
    args = parser.parse_args()

    execute_data_inspect_tool(parser, args)


if __name__ == "__main__":
    main()

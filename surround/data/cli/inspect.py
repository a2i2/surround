import os
import argparse

from ..container import DataContainer

def is_valid_file(parser, x):
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
    parser = argparse.ArgumentParser(description='Inspect the metadata and/or contents of a data container', add_help=False)

    parser.add_argument("container_file", type=lambda x: is_valid_file(parser, x), help="Path to the data container to inspect")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--metadata-only", action='store_true', help="Inspect the metadata of the container only")
    group.add_argument("-c", "--content-only", action='store_true', help="Inspect the contents of the container only")

    return parser

def perform_metadata_inspection(container):
    metadata = container.metadata
    print("Metadata format version: %s" % metadata['version'])
    print("Summary Metadata:")
    print("  Title:          %s" % metadata['summary']['title'])
    print("  Description:    %s" % metadata['summary']['description'])
    print("  Creator:        %s" % metadata['summary']['creator'])
    print("  Date:           %s" % metadata['summary']['date'])
    print("  Publisher:      %s" % metadata['summary']['publisher'])
    print("  Contributor:    %s" % metadata['summary']['contributor'])
    print("  Subject:        %s" % metadata['summary']['subject'])
    print("  Formats:        %s" % metadata['summary']['formats'])
    print("  Types:          %s" % metadata['summary']['types'])
    print("  Identifier:     %s" % metadata['summary']['identifier'])
    print("  Rights:         %s" % metadata['summary']['rights'])
    print("  Under Ethics:   %s" % metadata['summary']['under-ethics'])
    print("  Language:       %s" % metadata['summary']['language'])
    print()

    if metadata.get_property('manifests'):
        for manifest in metadata['manifests']:
            print("'%s' Group Metadata:" % manifest['path'])
            print("  Description:   %s" % manifest['description'])
            print("  Language:      %s" % manifest['language'])
            print("  Formats:       %s" % manifest['formats'])
            print("  Types:         %s" % manifest['types'])
            print()

def perform_content_inspection(container):
    print("Contents:")
    for content in container.get_files():
        print(content)

def execute_data_inspect_tool(parser, args):
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
    parser = get_data_inspect_parser()
    args = parser.parse_args()

    execute_data_inspect_tool(parser, args)

if __name__ == "__main__":
    main()

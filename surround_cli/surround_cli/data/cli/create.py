import os
import re
import argparse
import datetime
import mimetypes
import uuid

from ..metadata import Metadata
from ..container import DataContainer
from ..util import get_types_from_formats, prompt, split_unique

# Dictionary of language options (display_name, language_code)
language_options = [
    ("English", "en"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("Chinese", "zh"),
    ("Japanese", "ja"),
    ("Italian", "it"),
    ("Language not relevant", "N/A"),
    ("Other (ISO 639-1)", ""),
]

# List of options used when asking for rights
rights_options = ["Confidential", "Open", "Defence"]


def is_valid_file(parser, x):
    """
    Checks argument from parser is a valid file path

    :param parser: the parser
    :type parser: :class:`argparse.ArgumentParser`
    :param x: the value of the argument
    :type x: str
    :returns: the value if its valid, False otherwise
    :rtype: str or bool
    """

    if not os.path.exists(x) or os.path.isdir(x):
        parser.error("The file specified is not a file or doesn't exist!")
        return False

    return x


def is_valid_dir(parser, x):
    """
    Checks argument from parser is a valid directory path

    :param parser: the parser
    :type parser: :class:`argparse.ArgumentParser`
    :param x: the value of the argument
    :type x: str
    :returns: the value if its valid, False otherwise
    :rtype: str or bool
    """

    if not os.path.exists(x) or os.path.isfile(x):
        parser.error("The directory specified is not a directory or doesn't exist!")
        return False

    if not os.listdir(x):
        parser.error("The directory specified is empty!")
        return False

    return x


def is_valid_output_file(parser, x):
    """
    Checks argument from parser is a valid output file path (*.data.zip)

    :param parser: the parser
    :type parser: :class:`argparse.ArgumentParser`
    :param x: the value of the argument
    :type x: str
    :returns: the value if its valid, False otherwise
    :rtype: str or bool
    """

    if os.path.isdir(x):
        parser.error("The output argument must be a file path!")
        return False

    if os.path.exists(x):
        parser.error("The output file already exists!")
        return False

    split_path = os.path.splitext(x)
    if ".data" not in split_path[0] or split_path[1] != ".zip":
        parser.error("The output file must have the extension .data.zip")
        return False

    return x


def is_valid_json_output(parser, x):
    """
    Checks if argument given to parser is valid path to export to

    :param parser: the parser
    :type parser: :class:`argparse.ArgumentParser`
    :param x: the value of the argument
    :type x: str
    :returns: the value if its valid, False otherwise
    :rtype: str or bool
    """

    if not os.path.exists(os.path.dirname(os.path.abspath(x))):
        parser.error("Cannot export the metadata to that path!")
        return False

    return x


def get_data_create_parser():
    """
    Generates the parser used for the data container tool - create sub-command

    :returns: the parser generated
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(
        description="Create a data container from a file or directory", add_help=False
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--file",
        type=lambda x: is_valid_file(parser, x),
        help="Path to file to import into container",
    )
    group.add_argument(
        "-d",
        "--directory",
        type=lambda x: is_valid_dir(parser, x),
        help="Path to directory to import into container",
    )
    group.add_argument(
        "-m",
        "--metadata-only",
        action="store_true",
        help="Generate metadata without a file system",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=lambda x: is_valid_output_file(parser, x),
        help="Path to file to export container to (default: specified-path.data.zip)",
    )
    parser.add_argument(
        "-e",
        "--export-metadata",
        type=lambda x: is_valid_json_output(parser, x),
        help="Path to JSON file to export metadata to",
    )

    return parser


def validate_language_code(language_code):
    """
    Checks whether the language code given follows the ISO format, e.g "en"

    :param language_code: the string being checked
    :type language_code: str
    :returns: whether the code is valid
    :rtype: bool
    """

    return re.match("[a-z]{2}", language_code)


def prompt_language(default="en"):
    """
    Prompts the user on which language is most relevant to the data.
    Will return the default if the user skips the question.

    :param default: the language code that is default
    :type default: str
    :returns: the language code selected by the user
    :rtype: str
    """

    default_lang = next(
        (i + 1 for i, l in enumerate(language_options) if l[1] == default), 1
    )

    print("Language codes:")
    for i, option in enumerate(language_options):
        print(
            "%i. %s (%s) %s"
            % (
                i + 1,
                option[0],
                option[1] if option[1] != "" else "N/A",
                ("[DEFAULT]" if i + 1 == default_lang else ""),
            )
        )

    language = prompt(
        "Select the langauge most relevant to the data: ",
        help_msg="Select the language code most relevant to the contents, or select not relevant.",
        validator=lambda x: 0 < x <= len(language_options),
        answer_type=int,
        default=default_lang,
    )

    if "Other" in language_options[language - 1][0]:
        language = prompt(
            "Enter a language code following the ISO-639-1 standard: ",
            help_msg="Enter the ISO-639-1 representation of the language the data is in.",
            validator=validate_language_code,
        )
    else:
        language = language_options[language - 1][1]

    return language


def get_summary_metadata_from_user(metadata):
    """
    Prompts the user for the summary section of the metadata.
    Storing the results in the metadata instance provided.

    :param metadata: the metadata instance
    :type metadata: :class:`surround.data.metadata.Metadata`
    """

    print("============[Creating summary metadata]============")

    name = prompt(
        "What is your name: ",
        validator=lambda x: re.match("[A-Za-z]+", x),
        error_msg="Must contain letters only!",
        help_msg="Enter your full name, so you can be tracked down later if needed.",
    )

    title = prompt(
        "Give this data a short title: ",
        help_msg="Enter a short title that describes this data as a whole, e.g. Face Dataset",
    )

    description = prompt(
        "Provide a brief description of this data: ",
        help_msg="Enter a brief description of this data that describes it's contents and what it is used for.",
    )

    publisher = prompt(
        "What organisation is behind the creation of this data: ",
        help_msg="Enter the name of the organisation that created this data, so they can be tracked down later.",
    )

    contributor = prompt(
        "What is the name of the individual who sent you this data: ",
        validator=lambda x: re.match("[A-Za-z]+", x),
        error_msg="Must contain letters only!",
        help_msg="Enter the full name of the person who sent you this data, so they can be tracked down later.",
    )

    print(
        "When did they send you this data? Hit [ENTER] to use the current date & time."
    )
    print("Date formatting (ISO 8601): YYYY-MM-DDThh:mm")

    date_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"
    current_date = re.match(date_pattern, datetime.datetime.now().isoformat())
    current_date = current_date.group(0)

    date = prompt(
        "Date: ",
        help_msg="Enter the date & time you received this data, in the ISO format (YYYY-MM-DDThh:mm) - 24 hour time.",
        validator=lambda x: re.match(date_pattern, x),
        required=False,
        default=current_date,
    )

    subject = prompt(
        "List meaningful keywords related to this data (comma separated): ",
        help_msg="Enter a comma separated list of keywords that relate to the data, for example: faces, recognition, dogs, cats",
    )
    subject = split_unique(",| ,", subject, strip=True)

    language = prompt_language()

    print("Rights:")
    for i, right in enumerate(rights_options):
        print("%i. %s %s" % (i + 1, right, "[DEFAULT]" if i == 0 else ""))
    rights = prompt(
        "Select a right that fits the data: ",
        help_msg="Enter the number corresponding to the right that best fits what you are allowed to do with the data.",
        validator=lambda x: 0 < x < 5,
        answer_type=int,
        default=1,
    )
    rights = rights_options[rights - 1]

    under_ethics = prompt(
        "Is this data under any type of ethics (y/n): ",
        help_msg="Is this data under any ethical rules that make this data sensitive or impose any type of restrictions?",
        answer_type=bool,
    )

    metadata.set_property("summary.creator", name)
    metadata.set_property("summary.title", title)
    metadata.set_property("summary.date", date)
    metadata.set_property("summary.description", description)
    metadata.set_property("summary.publisher", publisher)
    metadata.set_property("summary.contributor", contributor)
    metadata.set_property("summary.subject", subject)
    metadata.set_property("summary.language", language)
    metadata.set_property("summary.rights", rights)
    metadata.set_property("summary.under-ethics", under_ethics)

    print("Summary metadata collection done!\n")


def get_metadata_for_group(manifest, default_lang, group_number, group_count):
    """
    Prompts the user for information on a single group of data (description and language).
    Stores the results in the manifest dictionary provided.

    :param manifest: the dictionary that will hold the answers
    :type manifest: dict
    :param default_lang: the default language code
    :type default_lang: str
    :param group_number: the position of the group in the list of groups
    :type group_number: int
    :param group_count: size of the group list
    :type group_count: int
    """

    print(
        "============[Creating individual metadata (%i/%i)]============"
        % (group_number, group_count)
    )
    print("Create metadata for group: %s\n" % manifest["path"])

    # Get answers from the user
    description = prompt(
        "Provide a breif description of this group: ",
        help_msg="Enter a breif description of this data that describes its contents and what it is used for.",
    )
    language = prompt_language(default_lang)

    # Set the manual fields to the manifest
    manifest["description"] = description
    manifest["language"] = language


def attempt_detect_sequences(metadata, root_files):
    """
    Try and detect a sequence of numbers in filenames of the root files e.g. image01.png, image02.png.
    If a group of 5 or more has been detected then prompt the user asking them if they want to create
    a group, if so then get a name and generate a manifest for this group.

    :param metadata: the instance of matadata
    :type metadata: :class:`surround.data.metadata.Metadata`
    :param root_files: list of files in the root folder
    :type root_files: list
    :returns: tuple containing name and list of files in group
    :rtype: (str, list)
    """

    print("Searching for potential sequential groups...\n")
    names = [(name, os.path.splitext(os.path.basename(name))[0]) for name in root_files]

    group = []
    for original_path, name in names:
        if re.match(r"^.*\d+$", name):
            group.append(original_path)

    if len(group) > 1:
        print("Possible sequential group of count %i detected!" % len(group))
        print("Here are the first few detected:")
        for name in group[:5]:
            print(name)
        print("...\n")

        name = prompt(
            "Enter a name if you would like to group them (or hit [ENTER] to skip): ",
            help_msg="Enter a name for the collection of files, the files will then be put in a folder of this name in the container.",
            required=False,
        )

        if name:
            # Create a manifest for the group in the metadata
            metadata.generate_manifest_for_group(name, group)
            return (name, group)

    return None


def attempt_detect_large_count(metadata, root_files):
    """
    Groups files in the root folder by extension, if a groups size is higher than 4
    then prompt the user to create a group for these files, collection a name for each group.

    :param metadata: the instance of metadata
    :type metadata: :class:`surround.data.metadata.Metadata`
    :param root_files: list of files in root directory
    :type root_files: list
    :returns: list of tuples with name and list of files in each group
    :rtype: list
    """

    unique_extensions = {os.path.splitext(x)[1] for x in root_files}

    groups = []
    for extension in unique_extensions:
        group = [f for f in root_files if os.path.splitext(f)[1] == extension]
        if len(group) > 4:
            print(
                "Possible group with %i files detected (via extensions)!" % len(group)
            )
            print("Here are the first few detected:")
            for name in group[:5]:
                print(name)
            print("...\n")

            name = prompt(
                "Enter a name if you would like to group them (or hit [ENTER] to skip): ",
                help_msg="Enter a name for the collection of files, the files will then be put in a folder of this name in the container.",
                required=False,
            )

            if name:
                # Create a manifest for this group
                metadata.generate_manifest_for_group(name, group)
                groups.append((name, group))

    return groups


def create_custom_groups(metadata, directory, existing_groups):
    """
    Prompt the user to enter a regex pattern to match groups of files.
    If matches are found, then it will prompt the user to enter a name
    for the group and add them to the metadata instance.

    :param metadata: metadata instance
    :type metadata: :class:`surround.data.metadata.Metadata`
    :param directory: path to the directory containing the files
    :type directory: str
    :param existing_groups: list of groups that already exist (name, list of files in group)
    :type existing_group: list
    :returns: the list of groups created (name, list of files in group)
    :rtype: list
    """

    print("============[Creating custom groups]================")
    groups = []
    while True:
        pattern = prompt(
            "Would you like to group files in the root by a regex pattern? If so enter one or press enter to skip: ",
            required=False,
        )

        if pattern:
            files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and re.match(pattern, f)
            ]

            if files:
                # Check if the files in this group aren't already in another, if so skip
                file_set = set(files)
                if any([bool(file_set & set(f)) for _, f in groups]) or any(
                    [bool(file_set & set(f)) for _, f in existing_groups]
                ):
                    print(
                        "This pattern matches with files in another group! Try again.\n"
                    )
                    continue

                print("Found %i files that follow this pattern!" % len(files))
                print("Here are the first few found:")
                for f in files[:5]:
                    print(os.path.basename(f))
                print("...")

                name = prompt(
                    "\nEnter a name for this group (or press enter to skip this group): ",
                    help_msg="Enter a name for the collection of files, the files will then be put in a folder of this name in the container.",
                    required=False,
                    validator=lambda x: not any(
                        [m["path"] == x for m in metadata["manifests"]]
                    ),
                    error_msg="This name is already taken! Please try again.",
                )

                if name:
                    # Create a manifest in the metadata for this group
                    metadata.generate_manifest_for_group(name, files)
                    groups.append((name, files))

            else:
                print("No files were found for that pattern, skipping...\n")

            # Continue to ask the user again
            continue

        # Stop asking the user when they skip
        break

    return groups


def get_metadata_for_groups(metadata, directory):
    """
    Handles the grouping section of the metadata collection process.
    First will check if there are any groups via file extension.
    If not then it will check if there are any groups via sequence.
    Then it will prompt the user to create groups via regex pattern.
    Lastly it will iterate through each manifest created for the groups
    and populate them with information from the user.

    :param metadata: the instance of metadata
    :type metadata: :class:`surround.data.metadata.Metadata`
    :param directory: path to directory containing files being imported
    :type directory: str
    :returns: list of groups created (name, list of files in group)
    :rtype: list
    """

    print("================[Attempting to auto-detect groups]===================")
    root_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    # Attempt to detect large numbers of the same extensions
    groups = attempt_detect_large_count(metadata, root_files)

    # If no extension groups found, try and find sequences in the file names
    if not groups:
        group = attempt_detect_sequences(metadata, root_files)
        if group:
            groups.append(group)

    # Create custom groups
    groups.extend(create_custom_groups(metadata, directory, groups))

    # Fill in metadata for folders & groups in the directory
    if metadata.get_property("manifests"):
        for i, manifest in enumerate(metadata["manifests"]):
            get_metadata_for_group(
                manifest,
                metadata["summary"]["language"],
                i + 1,
                len(metadata["manifests"]),
            )

    return groups


def generate_metadata_from_data(args):
    """
    Handles generating metadata from data being imported into a container.
    Using a combination of automatic and manually entered information from the user.

    :param args: the arguments given from the user
    :type args: :class:`argparse.Namespace`
    :returns: the metadata instance which holds all the collected info and a list of the groups created
    :rtype: :class:`surround.data.metadata.Metadata`, list
    """

    metadata = Metadata()

    # Get manual fields filled in by the user
    get_summary_metadata_from_user(metadata)

    # Generate automatic fields from specified file/folder
    if args.file:
        metadata.generate_from_file(args.file)
    else:
        metadata.generate_from_directory(args.directory)

        # Create groups based on patterns and get their individual metadata from the user
        groups = get_metadata_for_groups(metadata, args.directory)

    return metadata, groups


def is_valid_mime_type(mime_type):
    """
    Checks if mime type given is valid

    :param mime_type: value to check
    :type mime_type: str
    :returns: if the value is valid
    :rtype: bool
    """

    types = re.split(",| ,", mime_type)
    return all(
        [
            re.match(r"^.+/.+$", m) and m.strip() in mimetypes.types_map.values()
            for m in types
        ]
    )


def generate_metadata():
    """
    Handles generating an instance of metadata from user input ONLY.
    All fields that are usually generated automatically are prompted to
    the user.

    :returns: the instance of metadata created
    :rtype: :class:`surround.data.metadata.Metadata`
    """

    metadata = Metadata()

    # Get the manual fields fileld in by the user
    get_summary_metadata_from_user(metadata)

    # Get the formats and groups from the user since these can't be auto genereated
    formats = prompt(
        "What data formats make up the data? (MIME type e.g. text/plain)\nAnswer (comma separated): ",
        help_msg="Enter a comma separated list of MIME types that this data contains, e.g. text/plain, image/png",
        validator=is_valid_mime_type,
    )
    groups = prompt(
        "What groups (folders, collections) are in the data?\nAnswer (comma separated): ",
        help_msg="Enter a comma separated list of group names that this data contains, e.g. image, documents",
        required=False,
    )

    formats = [f.strip() for f in re.split(",| ,", formats)]
    types = get_types_from_formats(formats)

    # Set the formats and types to the summary metadata
    metadata.set_property("summary.formats", formats)
    metadata.set_property("summary.types", types)
    metadata.set_property("summary.identifier", str(uuid.uuid4()))

    if groups:
        groups = [g.strip() for g in re.split(",| ,", groups)]
        metadata.set_property("manifests", [])

        # Get all the metadata for each group
        for i, group in enumerate(groups):
            user_fields = {
                "description": None,
                "language": None,
            }

            # Get the description and language from the user
            get_metadata_for_group(
                user_fields, metadata["summary"]["language"], i + 1, len(groups)
            )

            # Get the formats from the user
            formats = prompt(
                "What data formats make up the group? (MIME type e.g. text/plain)\nAnswer (comma separated): ",
                help_msg="Enter a comma separated list of MIME types that this container will have. E.g. text/plain, image/png",
                validator=is_valid_mime_type,
            )
            formats = [f.strip() for f in re.split(",| ,", formats)]

            # Generate the manifest
            manifest = metadata.generate_manifest_for_group(group, [], formats)
            manifest["description"] = user_fields["description"]
            manifest["language"] = user_fields["language"]

    return metadata


def create_container(metadata, groups, args):
    """
    Generate a data container, importing the files specified by the supplied arguments
    and groups into the container, setting the metadata generated to the container and exporting
    the container to the specified output.

    :param metadata: the instance of metadata for this container
    :type metadata: :class:`surround.data.metadata.Metadata`
    :param groups: the groups created for this container
    :type groups: list
    :param args: the arguments provided by the user
    :type args: :class:`argparse.Namespace`
    """

    # If no output specified, use folder/file name with .data.zip as output path
    if not args.output:
        if args.file:
            output_file = os.path.splitext(args.file)[0] + ".data.zip"
        else:
            output_file = os.path.join(
                os.path.dirname(args.directory),
                os.path.basename(args.directory) + ".data.zip",
            )
    else:
        output_file = args.output

    # Import the data into a container
    container = DataContainer()
    container.metadata = metadata

    if args.directory:
        # Import the custom groups
        for name, files in groups:
            container.import_files(
                [(f, os.path.join(name, os.path.basename(f))) for f in files],
                generate_metadata=False,
            )

        # Import the entire directory (without re-importing the custom files)
        container.import_directory(
            args.directory, generate_metadata=False, reimport=False
        )
    else:
        # Import the single file
        container.import_file(
            args.file, os.path.basename(args.file), generate_metadata=False
        )

    print("Importing the data...")

    # Create the container
    container.export(output_file)

    print("Success! Data container exported to path %s" % output_file)


def execute_data_create_tool(parser, args):
    """
    Executes the data container CLI tool - create sub-command.
    Which packages a directory/file specified into a container and generates
    a metadata file containing information gathered from the user.

    :param parser: parser used to generate args
    :type parser: :class:`argparse.ArgumentParser`
    :param args: arguments suppled by the user
    :type args: :class:`argparse.Namespace`
    """

    # Ensure paths given are converted to absolute paths
    if args.file:
        args.file = os.path.abspath(args.file)
    elif args.directory:
        args.directory = os.path.abspath(args.directory)
    elif not args.export_metadata:
        print("error: --export-metadata argument required when using no data!")
        return

    if args.metadata_only:
        print("============[Creating data metadata]=============")
        print("Generating metadata...")
        print("Enter ? into fields for more information on how to answer.\n")

        metadata = generate_metadata()
    else:
        print("============[Creating a data container]============")
        print("Generating metadata...")
        print("Enter ? into fields for more information on how to answer.\n")
        metadata, groups = generate_metadata_from_data(args)

        print("Creating the container...")
        create_container(metadata, groups, args)

    # Export metadata to JSON file if requested
    if args.export_metadata:
        metadata.save_to_json_file(args.export_metadata)
        print("Exported the metadata to a JSON file: %s" % args.export_metadata)


def main():
    """
    Entry point that executes the create sub-command when this script is executed directly.
    """

    parser = get_data_create_parser()
    args = parser.parse_args()

    execute_data_create_tool(parser, args)


if __name__ == "__main__":
    main()

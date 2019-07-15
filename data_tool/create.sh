# Show the usage screen, since no arguments were given
if [[ $# -eq 0 ]] || [[ $1 == "--help" ]] || [[ $1 == "-h" ]]; then
    echo "usage: surround data create [-h] [-f FILE|-d DIRECTORY] [-o OUTPUT_FILE]"
    echo ""
    echo "Create a data container from a file or directory"
    echo ""
    echo "optional arguments:"
    echo "  -h, --help          show this help message and exit"
    echo "  -f FILE, --file FILE"
    echo "                      Path to file to import into container"
    echo "  -d DIRECTORY, --directory DIRECTORY"
    echo "                      Path to directory to import into container"
    echo "  -o OUTPUT, --output OUTPUT"
    echo "                      Path to file to export container to"

    exit 0
fi

# Get input file from user input (required)
if [[ $1 == "--file" ]] || [[ $1 == "-f" ]]; then
    if [[ $# -lt 2 ]]; then
        echo "--file argument requires a value"
        exit -1
    fi

    INPUT_FILE=$2
elif [[ $1 == "--directory" ]] || [[ $1 == "-d" ]]; then
    if [[ $# -lt 2 ]]; then
        echo "--directory argument requires a value"
        exit -1
    fi

    INPUT_DIR=$2
else
    echo "--file or --directory argument are required!"
fi

OUTPUT="./output.data.zip"

# Get output file from user input (no required)
if [[ $3 == "--output" ]] || [[ $3 == "-o" ]]; then
    if [[ $# -lt 4 ]]; then
        echo "--output requires a value"
    fi

    OUTPUT=$4
fi

function prompt() {
    echo "$1"
    read

    if [[ $# -ge 3 ]] && [[ -z $REPLY ]] && [[ -n $2 ]]; then
        echo "$2"
        echo "Enter ? for help on how to answer the field."
        echo ""
        prompt "$1" "$2" "$3"
        return
    fi

    if [[ $# -ge 3 ]] && [[ $REPLY == "?" ]]; then
        echo "$3"
        echo ""
        prompt "$1" "$2" "$3"
        return
    fi

    echo ""
}

# ============================== Generate Summary Metadata ============================
echo "=========[Creating a data container]========="

if [[ -n $INPUT_FILE ]]; then
    echo "Generating metadata for file: $INPUT_FILE"
else
    echo "Generating metadata for directory: $INPUT_DIR"
fi

echo ""
echo "======[Creating summary metadata]==========="
echo "Enter ? for help on how to answer the field."
echo ""
prompt "What is your name: " "This field is required!" "This field is required to identify who created the container later."
prompt "Give this data a short title describing its contents: " "This field is required!" "Just a short title that will help you identify the data quickly."
prompt "Give this data a brief description: " "This field is required!" "Provide a brief description of the contents of this data, to help people understand what it is used for etc.."
prompt "What organisation is behind the creation of this data: " "This field is required!" "Provide the name of the person/service that created and published this data. So the origin of the data is known."
prompt "What is the name of the individual who sent you this data:" "This field is required!" "Provide the name of the person who sent you this data. So they can be tracked down later if need be."
prompt "List meaningful keywords related to this data (comma separated):" "" "Provide a list of keywords that relate to this data, useful for quickly identifying the topic of the data."

echo "Language code of the data:"
echo "1. English (en) [DEFAULT]"
echo "2. Spanish (es)"
echo "3. French (fr)"
echo "4. Chinese (zh)"
echo "5. Japanese (ja)"
echo "6. Italian (it)"
echo "7. Other (ISO 639-1)"
prompt "Select the language most relevant to the data:" "" "Provide the language the data is in, the default is English."

echo "Rights:"
echo "1. Commercial [DEFAULT]"
echo "2. Open"
echo "3. Defence"
prompt "Select a right that fits the data:" "" "This is required so we know how to handle the data in terms of hosting online etc. The default is Commercial."

echo "Summary metadata collection done!"
echo ""

echo "Calculating hash... this may take a while"
sleep 2
echo "Done!"
echo ""

# ============================== Generate Individual Metadata ============================
function create_individual_metadata() {
    echo "===========[Create individual metadata]============="
    echo "Create metadata for $1: $2"
    echo ""

    prompt "Give this $1 a short title describing its contents: " "This field is required!" "Just a short title that will help you identify the data quickly."
    prompt "Give this $1 a brief description: " "This field is required!" "Provide a brief description of the contents of this data, to help people understand what it is used for etc.."
    prompt "What organisation is behind the creation of this $1: " "This field is required!" "Provide the name of the person/service that created and published this data. So the origin of the data is known."
    prompt "What is the name of the individual who sent you this $1:" "This field is required!" "Provide the name of the person who sent you this data. So they can be tracked down later if need be."
    prompt "List meaningful keywords related to this $1 (comma separated):" "" "Provide a list of keywords that relate to this data, useful for quickly identifying the topic of the data."

    echo "Language code of the data:"
    echo "1. English (en) [DEFAULT]"
    echo "2. Spanish (es)"
    echo "3. French (fr)"
    echo "4. Chinese (zh)"
    echo "5. Japanese (ja)"
    echo "6. Italian (it)"
    echo "7. Other (ISO 639-1)"
    prompt "Select the language most relevant to the $1:" "" "Provide the language the data is in, the default is English."
    
    if [[ $REPLY == "7" ]]; then
        prompt "Enter the ISO 669-1 language code:" "This is required!" "e.g. en for English"
    fi

    echo "Rights:"
    echo "1. Commercial [DEFAULT]"
    echo "2. Open"
    echo "3. Defence"
    prompt "Select a right that fits the $1:" "" "This is required so we know how to handle the data in terms of hosting online etc. The default is Commercial."
}

create_individual_metadata "folder" "IMAGES/"
create_individual_metadata "file" "INSTRUCTIONS.pdf"

echo "Creating container..."
echo "Success! Data container exported to path: $OUTPUT"
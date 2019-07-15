# Show the usage screen, since no arguments were given
if [[ $# -eq 0 ]] || [[ $1 == "--help" ]] || [[ $1 == "-h" ]]; then
    echo "usage: surround data inspect [-h] [-m|-c] CONTAINER"
    echo ""
    echo "Inspect the metadata and/or contents of a container"
    echo ""
    echo "positional arguments:"
    echo "  CONTAINER           Path to the data container to inspect"
    echo ""
    echo "optional arguments:"
    echo "  -h, --help          show this help message and exit"
    echo "  -m, --metadata-only inspect the metadata of the container only"
    echo "  -c, --content-only  inspect the contents of the container only"

    exit 0
fi

METADATA=1
CONTENT=1

if [[ -n $1 ]] && [[ $1 == "--metadata-only" || $1 == "-m" ]]; then
    CONTENT=0
fi

if [[ -n $1 ]] && [[ $1 == "--content-only" || $1 == "-c" ]]; then
    METADATA=0
fi

if [[ -n $2 && $# -ge 2 ]]; then
    DATA_CONTAINER=$2
elif [[ $# -eq 1 ]] && [[ METADATA -eq 1 && CONTENT -eq 1 ]]; then
    DATA_CONTAINER=$1
else
    echo "error: the positional argument CONTAINER is required"
    exit -1
fi

echo "========[Inspecting data in container]==========="
echo "Opening data container: $DATA_CONTAINER" 
echo ""

if [[ METADATA -eq 1 ]]; then
    echo "Summary Metadata:"
    echo "  version: 0.1"
    echo "  title: Ethnic Face Dataset"
    echo "  creator: Zac Brannelly"
    echo "  subject: faces, recognition, ethnic"
    echo "  description: Large collection of faces including instructions"
    echo "  publisher: Swinburne"
    echo "  contributor: Dr Karl (dr.karl@swin.edu.au)"
    echo "  date: 2019-09-15T15:53:00"
    echo "  types: StillImage"
    echo "  formats: image/jpeg, image/png"
    echo "  identifier: 059296ED5E1206BC3CD5FBD7B98C9B6E9EFC8BF7"
    echo "  source: None"
    echo "  language: en"
    echo "  rights: Open"
    echo ""
    echo "'data' Metadata (Directory):"
    echo "  title: Face Images"
    echo "  subject: faces, recognition, ethnic"
    echo "  description: The collection of ethnic faces"
    echo "  publisher: Swinburne"
    echo "  contributor: Dr Karl (dr.karl@swin.edu.au)"
    echo "  types: Collection, StillImage"
    echo "  formats: image/jpeg, image/png"
    echo "  identifier: 059296ED5E1206BC3CD5FBD7B98C9B6E9EFC8BF7"
    echo "  source: None"
    echo "  language: en"
    echo "  rights: Open"
    echo ""
    echo "'instructions.pdf' Metadata (File):"
    echo "  title: Loading Instructions"
    echo "  subject: documentation"
    echo "  description: Instructions on loading the data into Tensorflow"
    echo "  publisher: Swinburne"
    echo "  contributor: Dr Karl (dr.karl@swin.edu.au)"
    echo "  types: Text, StillImage"
    echo "  formats: application/pdf"
    echo "  identifier: 6BFEC6FBF46766746D147626A1EE3E99F2BA189C"
    echo "  source: None"
    echo "  language: en"
    echo "  rights: Open"
    echo ""
fi

if [[ CONTENT -eq 1 ]]; then
    echo "Contents:"
    echo "- data/"
    echo "--- image_01.png"
    echo "--- ..."
    echo "--- image_10000.png"
    echo "- instructions.pdf"
    echo ""
fi


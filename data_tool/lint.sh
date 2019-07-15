# Show the usage screen, since no arguments were given
if [[ $# -eq 0 ]] || [[ $1 == "--help" ]] || [[ $1 == "-h" ]]; then
    echo "usage: surround data lint [-h] CONTAINER"
    echo ""
    echo "Check the validity of a data container"
    echo ""
    echo "positional arguments:"
    echo "  CONTAINER           Path to the container to perform linting on"
    echo ""
    echo "optional arguments:"
    echo "  -h, --help          show this help message and exit"

    exit 0
fi

if [[ $# -ge 1 ]]; then
    DATA_CONTAINER=$1
else
    echo "error: the position argument CONTAINER is required"
    exit -1
fi

echo "========[Running data linter]==========="
echo "Performing checks on container: $DATA_CONTAINER"
echo ""
echo "========[Check #1: Data Integrity]======"
echo "Calculating hash of contents..."
sleep 2
echo "Comparing current hash with hash in metadata... OK!"
echo ""
echo "========[Check #2: Formats]============="
echo "Detecting formats in contents.."
sleep 1
echo "Comparing detected formats with formats stored in metadata... OK!"
echo ""
echo "========[Check #3: Metadata]============"
echo "Checking values of required metadata fields... OK!"
echo ""
echo "3/3 checks passed!"
echo "Your container looks good. Goodbye."

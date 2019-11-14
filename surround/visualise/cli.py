import argparse
import os
import json
import datetime
import pkg_resources
import pandas as pd

from ..config import Config
from .visualise_classifier import VisualiseClassifier, VisualiseClassifierData

def get_failed_set(y_true, y_pred):
    """
    Get incorrect/failed records from the ground truth & predict values.

    :param y_true: ground truth values
    :type y_true: iterable
    :param y_pred: predicted values
    :type y_pred: iterable
    :return: the culled y_true & y_pred lists
    :rtype: list, list
    """

    values = [(true, pred) for true, pred in zip(y_true, y_pred) if true != pred]
    true = [pair[0] for pair in values]
    pred = [pair[1] for pair in values]
    return true, pred

def is_valid_file(arg_parser, arg):
    """
    A simple function to validate a file path

    :param arg_parser: the parser using this function
    :type arg_parser: :class:`argparse.ArugmentParser`
    :param arg: the path we are checking
    :type arg: str
    """

    if not os.path.isfile(arg):
        arg_parser.error("Invalid file path %s" % arg)
        return arg
    return arg

def is_valid_directory(arg_parser, arg):
    """
    A simple function to validate a directory path

    :param arg_parser: the parser using this function
    :type arg_parser: :class:`argparse.ArugmentParser`
    :param arg: the path we are checking
    :type arg: str
    """

    if not os.path.isdir(arg):
        arg_parser.error("Invalid directory path %s" % arg)
        return arg
    return arg

def str2bool(v):
    """
    Convert string to boolean value. Used in boolean arguments.

    :param v: value we're converting
    :type v: str
    :return: the converted value
    :rtype: bool
    """

    if isinstance(v, bool):
        return v

    return v.lower() in ('yes', 'true', 't', 'y', '1')

def get_visualise_parser():
    """
    Returns the parser that describes the arguments used by the visualiser command line tool.

    :return: the parser
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(
        description='Visualise the output from a classifier.',
        epilog="Note: The first column in the --ground-truth flag maps to the frist column in the --predictions flag.")

    parser.add_argument("data_file", help="CSV file with ground truth and predicted labels", type=lambda x: is_valid_file(parser, x))

    parser.add_argument("-g", "--ground-truth", help="Comma separated list of columns containing ground truth values (default: ground_truth)", default="ground_truth")
    parser.add_argument("-p", "--predictions", help="Comma separated list of columns containing predictions (default: predictions)", default="predictions")
    parser.add_argument("-s", "--separater", help="File separator (default: ',')", default=",")
    parser.add_argument("--header", type=int, help="Row of the file to use as a header (default: 0)", default=0)
    parser.add_argument('-o', "--output-directory", help="Path to directory to export JSON/HTML results to", default=os.path.abspath("."), type=lambda x: is_valid_directory(parser, x))
    parser.add_argument('-i', '--output-incorrect', help="Output file containing incorrect records (default: true)", default=True, type=str2bool)
    parser.add_argument('-n', '--normalize', action="store_true", help="Show the normalized confusion matrix in reports")
    parser.add_argument('-no', '--no-output', action="store_true", help="Don't output reports to JSON/HTML files")
    parser.add_argument('-jo', '--json-only', action="store_true", help="Output visualisations to JSON files")
    parser.add_argument('-ho', '--html-only', action="store_true", help="Output visualisations to HTML files")

    return parser

def execute_visualise_tool(parser, args, extra_args):
    """
    Execute the visualiser tool using the arguments parsed from the user.

    :param parser: the parser used
    :type: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    # Get the ground truth and prediction column names from the users arguments
    ground_truth_columns = args.ground_truth.split(",")
    prediction_columns = args.predictions.split(",")

    if args.separater == "t":
        args.separater = '\t'

    # Read the CSV file and strip the headings of the columns
    file_contents = pd.read_csv(args.data_file, sep=args.separater, header=args.header, engine='python')
    file_contents.columns = [i.strip() for i in file_contents.columns]

    # Replace empty values with UNKNOWN
    file_contents.fillna(value="UNKNOWN", inplace=True)

    # Check if columns are present in data file
    for column in ground_truth_columns + prediction_columns:
        if column not in file_contents.columns:
            print("error: the column %s was not found in %s" % (column, args.data_file))
            print("Please check you have specified the right separator and/or column names")
            return

    # Initialise the visualiser
    visualiser = VisualiseClassifier()
    config = Config()
    config.read_from_dict({'show_normalized_confusion_matrix': args.normalize})

    results = []

    for i, _ in enumerate(ground_truth_columns):
        data = VisualiseClassifierData()
        data.y_true = file_contents[ground_truth_columns[i]]
        data.y_pred = file_contents[prediction_columns[i]]

        print("Results for columns %s & %s" % (ground_truth_columns[i], prediction_columns[i]))
        print("Ground truth column label: %s" % ground_truth_columns[i])
        print("Predict column label: %s" % prediction_columns[i])

        # Run the visualiser / display results in the terminal
        visualiser.visualise(data, config)

        print()

        # Keep the results in a list
        results.append({
            "input_file": os.path.basename(args.data_file),
            "ground_truth_label": ground_truth_columns[i],
            "predict_label": prediction_columns[i],
            "results": data.visualise_output
        })

    # If requested, generate a file containing only the incorrect data
    if args.output_incorrect and not args.no_output:
        export_incorrect_results(os.path.abspath(args.output_directory), file_contents, args.separater, ground_truth_columns, prediction_columns)

    # If requested, write results to an output file
    if not args.no_output:
        if not args.html_only:
            # Write the results to a JSON file
            export_results_json(results, os.path.abspath(args.output_directory))

        if not args.json_only:
            # Write the results to a HTML file
            export_results_html(results, os.path.abspath(args.output_directory), args.normalize)

def main():
    """
    The entry-point used for testing when the tool is being debugged.
    """

    # Get the parser used for this tool
    parser = get_visualise_parser()
    args = parser.parse_args()

    execute_visualise_tool(parser, args, [])

def export_incorrect_results(dir_path, file_contents, sep, ground_truth_columns, prediction_columns):
    """
    Export ONLY the incorrect values in the ground truth - predict value pairs.

    :param dir_path: folder where to put the file
    :type dir_path: str
    :param file_contents: the original data
    :type file_contents: :class:`pandas.DataFrame`
    :param sep: the separator used in the original CSV
    :type sep: str
    :param ground_truth_columns: column names of the ground truth values
    :type ground_truth_columns: list
    :param prediction_columns: column names of the prediction values
    :type prediction_columns: list
    """

    incorrect_records_df = pd.DataFrame(data=None, index=None, columns=ground_truth_columns + prediction_columns)

    for i, ground_truth_column in enumerate(ground_truth_columns):
        prediction_column = prediction_columns[i]
        y_true = file_contents[ground_truth_column]
        y_pred = file_contents[prediction_column]

        fail_true, fail_pred = get_failed_set(y_true, y_pred)
        df = pd.DataFrame({ground_truth_columns[i]: fail_true, prediction_columns[i]: fail_pred}, columns=[ground_truth_columns[i], prediction_columns[i]])
        incorrect_records_df = incorrect_records_df.append(df, sort=False)

    path = os.path.join(dir_path, 'incorrect_records.csv')
    incorrect_records_df.to_csv(path, index=None, header=True, sep='\t' if sep == '\\t' else sep)
    print("Exported incorrect values to file: %s" % path)

def export_results_json(results, output_dir):
    """
    Export each visualisation result into separate JSON files in the output directory.

    :param results: list of visualisation results
    :type results: list
    :param output_dir: directory where results should be saved
    :type output_dir: str
    """

    for data in results:
        # Write the results to a JSON file
        output_path = os.path.join(output_dir, "report_%s_%s.json" % (data["ground_truth_label"], data["predict_label"]))
        with open(output_path, "w+") as outfile:
            json.dump(data, outfile, indent=4)

        print("Exported a JSON report to file: %s" % output_path)

def export_results_html(results, output_dir, normalize):
    """
    Render HTML files visualising all of the results from the visualiser.
    A single HTML file will be generated per result with the filename results_g1_label_g2_label.html.

    :param results: results of the visualiser
    :type results: list
    :param output_dir: directory to export the HTML reports to
    :type output_dir: str
    """

    for data in results:
        # Generate HTML for overall and category metrics
        overall_metric_rows = generate_overall_metric_rows(data)
        category_metric_rows = generate_category_metric_rows(data)

        # Generate HTML report for data set using the report template
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualise_classifier_template.html.txt")
        with open(template_path, "r") as f:
            contents = f.read()
            new_contents = contents.format(
                conf_matrix=str(data["results"]["confusion_matrix" if not normalize else "normalized_confusion_matrix"]),
                class_list=str(data["results"]["classes"]),
                overall_rows=overall_metric_rows,
                category_rows=category_metric_rows,
                accuracy=data["results"]["accuracy_score"],
                cohen_kappa=data["results"]["cohen_kappa_score"],
                ground_truth_label=data["ground_truth_label"],
                predict_label=data["predict_label"],
                input_path=data["input_file"],
                date_string=datetime.datetime.now(),
                version='v%s' % pkg_resources.get_distribution('surround').version)

        # Write new HTML file to directory specified
        output_path = os.path.join(output_dir, "report_%s_%s.html" % (data["ground_truth_label"], data["predict_label"]))
        with open(output_path, "w+") as f:
            f.write(new_contents)

        print("Exported a HTML report to file: %s" % os.path.abspath(output_path))

def generate_overall_metric_rows(data):
    """
    Render HTML for an overall metrics table

    :param data: the results of the visualise operation
    :type data: dict
    :return: the HTML rendered
    :rtype: str
    """

    result = "<tr><td>Weighted Average</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["weighted avg"]["precision"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["weighted avg"]["recall"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["weighted avg"]["f1-score"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["weighted avg"]["support"])
    result += "</td></tr>\n"

    result += "<tr><td>Macro Average</td><td>\n"
    result += str(data["results"]["report"]["macro avg"]["precision"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["macro avg"]["recall"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["macro avg"]["f1-score"])
    result += "</td>\n"

    result += "<td>"
    result += str(data["results"]["report"]["macro avg"]["support"])
    result += "</td></tr>\n"

    return result

def generate_category_metric_rows(data):
    """
    Render HTML for a table showing metrics for all categories/classes.

    :param data: the visualisation data
    :type data: dict
    :return: the rendererd HTML
    :rtype: str
    """

    result = ""
    for category in data["results"]["classes"]:
        result += "<tr><td>"
        result += category
        result += "</td>\n"

        result += "<td>"
        result += str(data["results"]["report"][category]["accuracy"])
        result += "</td>\n"

        result += "<td>"
        result += str(data["results"]["report"][category]["precision"])
        result += "</td>\n"

        result += "<td>"
        result += str(data["results"]["report"][category]["recall"])
        result += "</td>\n"

        result += "<td>"
        result += str(data["results"]["report"][category]["f1-score"])
        result += "</td>\n"

        result += "<td>"
        result += str(data["results"]["report"][category]["support"])
        result += "</td></tr>\n"

    return result

if __name__ == "__main__":
    main()

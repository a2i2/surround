""" visualise.py

Visualises the output from training a classifier.

Supports both binary and multi class classifiers.

Use cases:
 - Visualising the output from training a model
 - Viewing the output from running batch predictions on a dataset

TODO: Order confusion matrix by most popular class to least popular class
TODO: Output file format in HTML. Always print to the screen.
TODO: Visualisation function should be different from function the output metrics
TODO: Wrap in a Visualiser interface for use in Surround
TODO: Support multiple ground truth and prediction columns
TODO: Add flag to output file with incorrect records. True by default.
TODO: Rename module to visualise_classifier.py

TODO: Add a flag to set probability thresholds
TODO: Add a flag that describes each aspect of the generated report in human readable terminology

"""

import pandas as pd
import argparse
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, cohen_kappa_score

def is_valid_file(arg_parser, arg):
    """A simple function to validate a file path"""
    if not os.path.isfile(arg):
        arg_parser.error("Invalid file path %s" % arg)
        return arg
    return arg

def calculate(dataframe, ground_truth, predictions):
    dataframe.fillna(value="UNKNOWN", inplace=True)
    print(classification_report(dataframe[ground_truth], dataframe[predictions]))
    print(confusion_matrix(dataframe[ground_truth], dataframe[predictions]))
    print("Accuracy: %s" % accuracy_score(dataframe[ground_truth], dataframe[predictions]))
    print("Cohen Kappa: %s" % cohen_kappa_score(dataframe[ground_truth], dataframe[predictions]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description=
            'Visualise the output from a classifier.',
    epilog="Note: The first column in the --ground-truth flag maps to the frist column in the --predictions flag.")

    parser.add_argument("data_file", help="CSV file with ground truth and predicted labels", type=lambda x: is_valid_file(parser, x))

    parser.add_argument("-g", "--ground-truth", help="Comma separated list of columns containing ground truth values", default="ground_truth")
    parser.add_argument("-p", "--predictions", help="Comma separated list of columns containing predictions", default="predictions")
    parser.add_argument("-s", "--separater", help="File separator", default=",")
    parser.add_argument("-t", "--title-header", type=int, help="Row of the file to use as a header", default=0)

    args = parser.parse_args()

    ground_truth_columns = args.ground_truth.split(",")
    prediction_columns = args.predictions.split(",")

    error = False
    if len(ground_truth_columns) != len(prediction_columns):
        print("Prediction columns should be the same length as the ground truth columns.")
        error = True

    file_contents = pd.read_csv(args.data_file, sep=args.separater, header=args.title_header)
    headers = [i.strip() for i in file_contents.columns]
    file_contents.columns = headers

    for i in ground_truth_columns:
        if not i in headers:
            print("Ground truth column missing from the data file: %s" % i)
            error = True

    for i in prediction_columns:
        if not i in headers:
            print("Prediction column missing from the data file: %s" % i)
            error = True

    if not error:
        calculate(file_contents, ground_truth_columns[0], prediction_columns[0])

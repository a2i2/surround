""" visualise.py

Visualises the output from training a classifier.

Supports both binary and multi class classifiers.

Use cases:
 - Visualising the output from training a model
 - Viewing the output from running batch predictions on a dataset

TODO: Add a flag to set probability thresholds
TODO: Add a flag that describes each aspect of the generated report in human readable terminology

"""

import numpy as np

from surround.state import State
from surround.stage import Stage

class VisualiseClassifierData(State):
    """
    The data object used when running the VisualiseClassifier in the command line.
    """

    y_true = []
    y_pred = []
    visualise_output = {}

class VisualiseClassifier(Stage):
    """
    Classification visualiser stage. Generates metrics based on a column of ground truth values
    and predicted values to help you evaluate the performance of the estimator.

    .. note:: This stage requires the state object to have ``y_true``, ``y_pred`` and ``visualise_output`` fields.
            Where the ``visualise_output`` field must be a dictionary and the other two lists of values.
    """

    def validate(self, state):
        """
        Validate the data given to the visualiser. Checks whether we have the required fields
        to perform visualisation.

        :param state: the object containing the data to visualise
        :type state: :class:`surround.State`
        :param config: the configuration of the current pipeline
        :type config: :class: `surround.Config`
        :return: Whether the data needed is valid
        :rtype: bool
        """

        if not state.y_true.empty:
            state.errors.append("No ground truth data provided.")

        if not state.y_pred.empty:
            state.errors.append("No prediction data provided.")

        if not state.errors and len(state.y_true) != len(state.y_pred):
            state.errors.append("Length of ground truth data and prediction data mismatch")

        if not state.visualise_output:
            state.errors.append("No field defined for the output of the visualiser")

        return len(state.errors) > 0

    def generate_table_from_report(self, report_dict, classes):
        """
        Generate a table containing the metrics per class.

        :param report_dict: the dictionary containing the metric values
        :type report_dict: dict
        :parama classes: list of classes in the data
        :type classes: list
        :return: the table
        :rtype: str
        """

        template = "{:8}|{:10}|{:10}|{:10}|{:10}|{:10}\n"
        result = template.format("", "accuracy", "precision", "recall", "f1-score", "support")

        for category in classes:
            values = report_dict[category]
            result += template.format(
                category,
                "{:.2f}".format(values['accuracy']),
                "{:.2f}".format(values['precision']),
                "{:.2f}".format(values['recall']),
                "{:.2f}".format(values['f1-score']),
                "{:.2f}".format(values['support']))

        return result

    def generate_table_from_overall_report(self, report_dict):
        """
        Generate a table containing the overall metrics.

        :param report_dict: the dictionary containing the metric values
        :type report_dict: dict
        :return: the table
        :rtype: str
        """

        template = "{:14}|{:10}|{:10}|{:10}\n"
        result = template.format("", "precision", "recall", "f1-score")

        macro_avg = report_dict['macro avg']
        result += template.format(
            "macro avg",
            "{:.2f}".format(macro_avg['precision']),
            "{:.2f}".format(macro_avg['recall']),
            "{:.2f}".format(macro_avg['f1-score']))

        weighted_avg = report_dict['weighted avg']
        result += template.format(
            "weighted avg",
            "{:.2f}".format(weighted_avg['precision']),
            "{:.2f}".format(weighted_avg['recall']),
            "{:.2f}".format(weighted_avg['f1-score']))

        return result

    def operate(self, surround_data, config):
        """
        Visualises the classifier data, calculating metrics such as accuracy, precision, cohen_kappa,
        f1-score and a confusion matrix. Prints the results to the terminal.

        :param state: the data being visualised
        :type state: :class:`surround.State`
        :param config: the config of the pipeline
        :type config: :class:`surround.Config`
        """

        if not self.validate(surround_data):
            for error in surround_data.errors:
                print("ERROR: " + error)
            return

        # Calculate metrics using the y_true and y_pred values
        surround_data.visualise_output = calculate_classifier_metrics(surround_data.y_true, surround_data.y_pred)

        report_dict = surround_data.visualise_output['report']
        classes = surround_data.visualise_output['classes']
        conf_matrix = surround_data.visualise_output['confusion_matrix']
        norm_conf_matrix = surround_data.visualise_output['normalized_confusion_matrix']

        # Generate pretty tables for the console
        overall_metrics = self.generate_table_from_overall_report(report_dict)
        per_category_table = self.generate_table_from_report(report_dict, classes)

        print("============[Classification Report]===================")
        print("Overall Metrics:")
        print(overall_metrics)
        print("Accuracy: %s" % surround_data.visualise_output['accuracy_score'])
        print("Cohen Kappa: %s" % surround_data.visualise_output['cohen_kappa_score'])
        print("==========================")
        print("Metrics per category:")
        print(per_category_table)
        print("==========================")
        print("Confusion Matrix:")

        # Print header of confusion matrix
        max_len = max([len(c) for c in classes])
        print(("{:>{:}} " + "{:^8} " * len(classes)).format("", max_len, *classes))

        # Print rows of confusion matrix, with labels
        template = "{:>{:}}|" + "{:^8}|" * len(classes)
        cm = conf_matrix if not config['show_normalized_confusion_matrix'] else norm_conf_matrix
        for i, _ in enumerate(classes):
            print(template.format(classes[i], max_len, *cm[i]))

        print("============[End of visualisation]===================")

def safe_div(a, b):
    return a / b if b else 0

def classification_report(y_true, y_pred, classes):
    results = {}

    for name in classes:
        tp = len([(yt, yp) for yt, yp in zip(y_true, y_pred) if yt == yp and yt == name])
        fp = len([(yt, yp) for yt, yp in zip(y_true, y_pred) if yt != yp and yp == name])
        fn = len([(yt, yp) for yt, yp in zip(y_true, y_pred) if yt != yp and yt == name])

        precision = safe_div(tp, (tp + fp))
        recall = safe_div(tp, tp + fn)
        f1_score = safe_div(2 * tp, 2 * tp + fp + fn)
        support = len([p for p in y_true if p == name])
        accuracy = safe_div(tp, fp + fn + tp)

        results[name] = {
            "precision": precision,
            "recall": recall,
            "f1-score": f1_score,
            "support": support,
            "accuracy": accuracy
        }

    total_tp_plus_tn = len([(yt, yp) for yt, yp in zip(y_true, y_pred) if yt == yp])
    results["accuracy"] = safe_div(total_tp_plus_tn, len(y_true))

    results["macro avg"] = {
        "precision": np.mean([results[name]["precision"] for name in classes]),
        "recall": np.mean([results[name]["recall"] for name in classes]),
        "f1-score": np.mean([results[name]["f1-score"] for name in classes]),
        "support": len(y_true),
    }

    weights = [results[name]["support"] for name in classes]

    results["weighted avg"] = {
        "precision": np.average([results[name]["precision"] for name in classes], weights=weights),
        "recall": np.average([results[name]["recall"] for name in classes], weights=weights),
        "f1-score": np.average([results[name]["f1-score"] for name in classes], weights=weights),
        "support": len(y_true),
    }

    return results

def calculate_confusion_matrix(y_true, y_pred, classes):
    result = np.empty([len(classes), len(classes)], dtype=np.int)
    pairs = list(zip(y_true, y_pred))

    for i, true_label in enumerate(classes):
        for j, pred_label in enumerate(classes):
            result[i][j] = pairs.count((true_label, pred_label))

    return result

def calculate_cohen_kappa(confusion_matrix):
    n_classes = confusion_matrix.shape[0]
    sum0 = np.sum(confusion_matrix, axis=0)
    sum1 = np.sum(confusion_matrix, axis=1)
    expected = safe_div(np.outer(sum0, sum1), np.sum(sum0))

    w_mat = np.ones([n_classes, n_classes], dtype=np.int)

    # pylint: disable=unsupported-assignment-operation
    w_mat.flat[:: n_classes + 1] = 0

    k = safe_div(np.sum(w_mat * confusion_matrix), np.sum(w_mat * expected))
    return 1 - k

def calculate_classifier_metrics(y_true, y_pred):
    """
    Calculate the metrics used for the classifier visualiser.

    :param y_true: ground truth values
    :type y_true: iterable
    :param y_pred: predicted values
    :type y_pred: iterable
    :return: report, confusion matrix, accuracy, cohen kappa, classes
    :rtype: dict
    """

    classes = list(set(y_true).union(set(y_pred)))

    # Ensure all values are strings
    classes = [str(c) for c in classes]
    y_true = [str(y) for y in y_true]
    y_pred = [str(y) for y in y_pred]

    report_dict = classification_report(y_true, y_pred, classes)
    accuracy = report_dict["accuracy"]

    # Generate a sorted class list and confusion matrix (sorted by popular class)
    if isinstance(y_true, list):
        y_true_list = y_true
    else:
        y_true_list = y_true.tolist()

    classes = sorted(classes, key=y_true_list.count, reverse=True)
    conf_matrix = calculate_confusion_matrix(y_true, y_pred, classes)
    normal_conf_matrix = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis]
    normal_conf_matrix = np.nan_to_num(normal_conf_matrix)

    cohen_kappa = calculate_cohen_kappa(conf_matrix)

    output = {
        'report': report_dict,
        'confusion_matrix': conf_matrix.tolist(),
        'normalized_confusion_matrix': normal_conf_matrix.tolist(),
        'accuracy_score': accuracy,
        'cohen_kappa_score': cohen_kappa,
        'classes': classes
    }

    return round_dict(output, 4)

def round_dict(data, n_digits):
    """
    Recursively round all floats in a dictionary to n digits.

    :param data: the dictionary
    :type data: dict
    :param n_digits: amount of digits to round to
    :type n_digits: int
    :return: the dictionary with values rounded
    :rtype: dict
    """

    result = data.copy()

    for key, value in data.items():
        if isinstance(value, float):
            result[key] = round(value, n_digits)
        elif isinstance(value, dict):
            result[key] = round_dict(value, n_digits)
        elif isinstance(value, list):
            result[key] = round_list(value, n_digits)

    return result

def round_list(data, n_digits):
    """
    Recursively round all floats in a list to n digits.

    :param data: the list to round
    :type data: list
    :param n_digits: amount of digits to round to
    :type n_digits: int
    :return: the list with values rounded
    :rtype: list
    """

    result = data.copy()

    for i, value in enumerate(data):
        if isinstance(value, float):
            result[i] = round(value, n_digits)
        elif isinstance(value, list):
            result[i] = round_list(value, n_digits)

    return result

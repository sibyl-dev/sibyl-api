import numpy as np


def get_rows_by_output(output, predict, x, row_labels=None, transformer=None):
    """
    Return the indices of the rows in x that get predicted as output

    :param output: int or array-like
           The output or outputs to look for
    :param predict: function array-like (x.shape) -> (x.shape[0])
           The prediction function
    :param x: Dataframe of shape(n_samples, n_features)
           The data to look through
    :param row_labels: None or array_like of shape (n_samples,)
           If not None, return the row_labels of relevant rows instead of
           numerical indices
    :param transformer: Transformer to use before running model
    :return: array_like
            The indices or row_labels of the rows of x that result in output
            when run through predict
    """
    if transformer is not None:
        x = transformer.transform(x)
    preds_train = predict(x)
    if np.isscalar(output):
        output = [output]
    xs_of_interest = np.isin(preds_train, output)
    if row_labels is None:
        row_labels = np.arange(0, len(xs_of_interest))
    else:
        row_labels = np.asanyarray(row_labels)
    return row_labels[xs_of_interest]


def summary_categorical(X):
    """
    Returns the unique values and counts for each column in x
    :param X: array_like of shape (n_samples, n_features)
           The data to summarize
    :return values: list of length n_features of arrays
                    The unique values for each feature
    :return count: list of length n_features
                   The number of occurrences of each unique value
                   for each feature
    """
    all_values = []
    all_counts = []
    X = np.asanyarray(X)
    for col in X.T:
        values, counts = np.unique(col, return_counts=True)
        all_values.append(values)
        all_counts.append(counts)
    return all_values, all_counts


def summary_numeric(X):
    """
    Find the minimum, 1st quartile, median, 2nd quartile, and maximum of the
    values for each column in x
    :param X: array_like of shape (n_samples, n_features)
           The data to summarize
    :return: A list of length (n_features) of lists of length 5
             The metrics for each feature:
             [minimum, 1st quartile, median, 2nd quartile, and maximum]
    """
    all_metrics = []
    X = np.asanyarray(X)
    for col in X.T:
        quartiles = np.quantile(col, [0.25, 0.5, 0.75])
        maximum = col.max()
        minimum = col.min()
        all_metrics.append([float(minimum), float(quartiles[0]), float(quartiles[1]),
                            float(quartiles[2]), float(maximum)])
    return all_metrics

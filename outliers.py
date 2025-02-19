import math
import statistics


def grubbs_test(data, alpha=0.05):
    """
    Perform Grubbs' test to detect a single outlier in a dataset.
    Args:
        data (list): The dataset to test.
        alpha (float): Significance level (default is 0.05).
    Returns:
        index (int): Index of the detected outlier, or -1 if no outlier.
        G (float): Grubbs' test statistic for the detected outlier.
    """
    n = len(data)
    if n < 3:
        raise ValueError("Grubbs' test requires at least 3 data points.")

    data_mean = statistics.mean(data)
    data_stdev = statistics.stdev(data)

    max_diff = max(abs(x - data_mean) for x in data)
    G = max_diff / data_stdev

    # Compute the critical value for Grubbs' test
    t_critical = abs(math.sqrt((n - 1) * (1 - alpha / (2 * n))) / math.sqrt(n - 2 + (n - 1)))
    G_critical = ((n - 1) / math.sqrt(n)) * t_critical

    if G > G_critical:
        return data.index(max(data, key=lambda x: abs(x - data_mean))), G
    return -1, G

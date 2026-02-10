import math
import statistics


def grubbs_test(data, datum, alpha=0.05):
    """
    Perform Grubbs' test to detect a single outlier in a dataset.
    Args:
        data (list): The dataset to test.
        datum (float): The datum to test as a potential outlier.
        alpha (float): Significance level (default is 0.05).
    Returns:
        outlier (bool): Whether datum is an outlier.
    """
    n = len(data)
    if n < 3:
        return False  # Grubbs' test requires ≥3 data points to determine an outlier

    data_mean = statistics.mean(data)
    data_stdev = statistics.stdev(data)
    if data_stdev == 0:
        return -1, 0.0

    datum_diff = abs(datum - data_mean)
    g = datum_diff / data_stdev

    # Compute the critical value for Grubbs' test
    t_critical = abs(math.sqrt((n - 1) * (1 - alpha / (2 * n))) / math.sqrt(n - 2 + (n - 1)))
    g_critical = ((n - 1) / math.sqrt(n)) * t_critical

    return g > g_critical

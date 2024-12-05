import math
import statistics


def mean_concentrations(concs):
    conc_clusters = clusterize(concs)
    means = []

    for cluster in conc_clusters:
        outlier, _ = grubbs_test(cluster)
        if outlier > -1:
            del cluster[outlier]
        avg = statistics.mean(cluster)
        means.append(avg)

    return means


def stdev_concentrations(concs):
    conc_clusters = clusterize(concs)
    stdevs = []

    for cluster in conc_clusters:
        outlier, _ = grubbs_test(cluster)
        if outlier > -1:
            del cluster[outlier]
        avg = statistics.stdev(cluster)
        stdevs.append(avg)

    return stdevs


def clusterize(data):
    clusters = []
    rows = len(data)
    cols = len(data[0]) if rows > 0 else 0

    for i in range(0, rows - 1, 2):
        for j in range(0, cols - 1, 2):
            clusters.append([data[i][j], data[i][j + 1], data[i + 1][j], data[i + 1][j + 1]])

    return clusters


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

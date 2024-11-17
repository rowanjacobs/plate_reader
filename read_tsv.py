from datetime import datetime


def read_data(lines):
    return [[float(x) for x in line.split()[2:]] for line in lines[1:]]


def read_statistics(lines):
    return {
        'Max V': [float(x) for x in lines[1].split()[1:5]],
        'R-Squared': [float(x) for x in lines[2].split()[:4]],
        't at Max V': [time_in_seconds(x) for x in lines[3].split()[:4]],
        'Lagtime': [time_in_seconds(x) for x in lines[4].split()[:4] if x != '?????']
    }


def time_in_seconds(time_str):
    time_format = "%H:%M:%S"
    return (datetime.strptime(time_str, time_format) - datetime(1900, 1, 1)).seconds

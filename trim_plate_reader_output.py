import re

data_line_pattern = r"^\d{1,2}:\d{2}:\d{2}\t\d+(\.\d+)?"


def trim_plate_reader_output(lines):
    data_start = 0
    data_end_offset = 0

    for i, line in enumerate(lines):
        if line.startswith('Time\tT∞'):
            data_start = i
            break

    for i, line in enumerate(reversed(lines)):
        if re.match(data_line_pattern, line):
            data_end_offset = i
            break

    return lines[data_start:-data_end_offset], lines[-data_end_offset+2:]

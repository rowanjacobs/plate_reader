import argparse
import csv

import read_tsv
import replicate_set_timeline
import trim_plate_reader_output


def process_file(lines, single_line=False):
    data_lines, _ = trim_plate_reader_output.trim_plate_reader_output(lines)
    if single_line:
        data = read_tsv.data_into_replicate_set_timelines_single_line(data_lines)
    else:
        data = read_tsv.data_into_replicate_set_timelines(data_lines)
    return replicate_set_timeline.generate_timeline_table(data)


def write_output(data_rows, output_file):
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        for row in data_rows:
            print(row)
            writer.writerow(row)


def read_plate_file(input_file):
    # the plate reader produces output in iso-8859-1 format.
    # attempting to parse it as Unicode will result in serious errors.
    with open(input_file, 'r', encoding='iso-8859-1') as infile:
        lines = infile.readlines()
    return lines


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Process a plate reader data file into absorbance data")

    # Define the arguments
    parser.add_argument('input', type=str, help="The input file to be processed")
    parser.add_argument('output', type=str, help="The location to write the processed absorbance data")
    parser.add_argument('--single-line', action='store_true',
                        help="Set this flag to disable grouping wells into replicate sets.")

    # Parse the arguments
    args = parser.parse_args()

    lines = read_plate_file(args.input)

    data_rows = process_file(lines, args.single_line)

    write_output(data_rows, args.output)


if __name__ == '__main__':
    main()

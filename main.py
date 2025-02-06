import csv

import absorbance
import apply_statistics
import read_tsv
import replicate_set
import replicate_set_timeline
import trim_plate_reader_output

import argparse


def process_file(input_file, output_file, single_line=False):
    # Process:
    # 1. read plate reader file
    # 2. trim non-data lines, saving off statistical lines
    # 3. read data lines as TSV
    # 4. read statistical lines as TSV
    # 5. apply Beer's law
    # 6. write output to file(s)

    with open(input_file, 'r', encoding='iso-8859-1') as infile:
        lines = infile.readlines()

    data_lines, _ = trim_plate_reader_output.trim_plate_reader_output(lines)
    if single_line:
        data = read_tsv.data_into_replicate_set_timelines_single_line(data_lines)
    else:
        data = read_tsv.data_into_replicate_set_timelines(data_lines)
    data_rows = replicate_set_timeline.generate_timeline_table(data)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        for row in data_rows:
            print(row)
            writer.writerow(row)


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

    # Call the processing function with the input and output file paths
    process_file(args.input, args.output, args.single_line)


if __name__ == '__main__':
    main()

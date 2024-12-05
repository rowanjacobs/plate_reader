import csv

import absorbance
import apply_statistics
import read_tsv
import trim_plate_reader_output

import argparse


def process_file(input_file, output_file, stats_file=None):
    # Process:
    # 1. read plate reader file
    # 2. trim non-data lines, saving off statistical lines
    # 3. read data lines as TSV
    # 4. read statistical lines as TSV
    # 5. apply Beer's law
    # 6. write output to file(s)

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    data_lines, _ = trim_plate_reader_output.trim_plate_reader_output(lines)
    data = read_tsv.read_data(data_lines)
    concentration_data = absorbance.concentration_of_array(data)
    data_cluster_means = apply_statistics.mean_concentrations(concentration_data)
    data_cluster_stdevs = apply_statistics.stdev_concentrations(concentration_data)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        writer.writerow(["Mean concentration", "Stdev"])
        for row in zip(data_cluster_means, data_cluster_stdevs):
            writer.writerow(row)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Process a plate reader data file into absorbance data")

    # Define the arguments
    parser.add_argument('input', type=str, help="The input file to be processed")
    parser.add_argument('output', type=str, help="The location to write the processed absorbance data")

    # Parse the arguments
    args = parser.parse_args()

    # Call the processing function with the input and output file paths
    process_file(args.input, args.output, args.stats)


if __name__ == '__main__':
    main()

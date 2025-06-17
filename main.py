import argparse
import csv

import read_tsv
import replicate_set_timeline
import trim_plate_reader_output

from os import listdir
from os.path import isfile, join, basename


def process_file(lines, single_line=False, filename=''):
    data_lines, _ = trim_plate_reader_output.trim_plate_reader_output(lines)
    if single_line:
        data = read_tsv.data_into_replicate_set_timelines_single_line(data_lines, filename=filename)
    else:
        try:
            data = read_tsv.data_into_replicate_set_timelines(data_lines, filename=filename)
        except IndexError as e:
            if filename != '':
                print(f'Error in parsing {filename}')
            print(e)
            data = read_tsv.data_into_replicate_set_timelines_single_line(data_lines, filename=filename)
    # TODO there should be some option for outputting avg conc data as well
    return data


def write_output(data_rows, output_file, mode='w'):
    with open(output_file, mode, newline='') as outfile:
        writer = csv.writer(outfile)

        for row in data_rows:
            writer.writerow(row)


def read_plate_file(input_file):
    # the plate reader produces output in iso-8859-1 format.
    # attempting to parse it as Unicode will result in serious errors.
    with open(input_file, 'r', encoding='iso-8859-1') as infile:
        lines = infile.readlines()
    return lines


def output_plots(data, output):
    if isfile(output):
        # TODO get parent dir of output filename
        raise ValueError(f"Output '{output}' is not a directory")
    for rstl in data:
        fig = rstl.plot()
        fig.savefig(join(output, rstl.well))


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Process a plate reader data file into absorbance data")

    # Define the arguments
    parser.add_argument('input', nargs='?', type=str, help="The input file to be processed", default="input")
    parser.add_argument('output', type=str, help="The location to write the processed absorbance data")
    parser.add_argument('--single-line', action='store_true',
                        help="Set this flag to disable grouping wells into replicate sets.")
    parser.add_argument('--megamix', action='store_true',
                        help="Set this flag to process *all* input files in input directory")
    parser.add_argument('--plot-data', action='store_true',
                        help="Set this flag to output plots of raw data and fits for each well group, in a separate "
                             "file in the output directory")

    # Parse the arguments
    args = parser.parse_args()

    if args.megamix:
        input_files = [f for f in listdir(args.input) if isfile(join(args.input, f)) and f != '.DS_Store']

        files_data = {f: process_file(read_plate_file(join(args.input, f)), args.single_line, filename=f) for f in
                      input_files}

        files_rows = [replicate_set_timeline.generate_fit_table(files_data[f], f) for f in files_data]

        final_rows = [["filename", "well", "Km", "kcat", "kcat/Km"]] + [x for xs in files_rows for x in xs]

        # TODO also write a file with absorbance
        # TODO also output plots of data with fit plots (using matplotlib)
        write_output(final_rows, args.output, mode='a')

    else:
        lines = read_plate_file(args.input)

        data = process_file(lines, args.single_line)

        data_rows = replicate_set_timeline.generate_fit_table(data) + replicate_set_timeline.generate_timeline_table(
            data)

        data_rows = [["well", "Km", "kcat", "kcat/Km"]] + data_rows

        output_file = args.output
        if not isfile(args.output):
            output_file = join(args.output, basename(args.input).replace('.txt', '.csv'))
        write_output(data_rows, output_file)

        if args.plot_data:
            output_plots(data, args.output)


if __name__ == '__main__':
    main()

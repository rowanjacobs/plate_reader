import argparse
import csv

import metabolite_naming
import read_tsv
import replicate_set_timeline
import trim_plate_reader_output

from os import listdir
from os.path import isfile, join, basename

import matplotlib.pyplot as plt


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
    with open(output_file, mode, newline='', encoding="utf-8") as outfile:
        # write a UTF-8 BOM to force Excel to read the output as UTF-8
        outfile.write('\ufeff')

        writer = csv.writer(outfile)

        for row in data_rows:
            writer.writerow(row)


def read_plate_file(input_file):
    # the plate reader produces output in iso-8859-1 format.
    # attempting to parse it as Unicode will result in serious errors.
    with open(input_file, 'r', encoding='iso-8859-1') as infile:
        lines = infile.readlines()
    return lines


def output_plot(rstl, dirname, unbundle=False, title=''):
    if unbundle:
        fig = rstl.bundle_plot(title_override=f'{title}')
    else:
        fig = rstl.plot(title_override=f'{title}')
    fig.savefig(join(dirname, title + '.png'))
    plt.close(fig)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Process a plate reader data file into absorbance data")

    # Define the arguments
    parser.add_argument('input', nargs='?', type=str, help="The input file to be processed", default="input")
    parser.add_argument('output', type=str, help="The location to write the processed absorbance data")
    parser.add_argument('--single-line', action='store_true',
                        help="Set this flag to disable grouping wells into replicate sets.")
    parser.add_argument('--single-file', action='store_true',
                        help="Set this flag to process a single file instead of *all* files in input directory")
    parser.add_argument('--bundle', action='store_true',
                        help="Set this flag to average wells before curve fitting")
    # TODO remove this entirely but make sure old scripts don't break
    parser.add_argument('--unbundle', action='store_true',
                        help="(deprecated flag, does nothing)")
    parser.add_argument('--plot-data', action='store_true',
                        help="(deprecated flag, does nothing)")
    parser.add_argument('--megamix', action='store_true',
                        help="(deprecated flag, does nothing)")

    # Parse the arguments
    args = parser.parse_args()

    if not args.single_file:
        if isfile(args.output):
            # TODO get parent dir of output filename
            raise ValueError(f"Output '{args.output}' is not a directory")

        input_files = [f for f in listdir(args.input) if isfile(join(args.input, f)) and f != '.DS_Store']

        files_data = {f: process_file(read_plate_file(join(args.input, f)), args.single_line, filename=f) for f in
                      input_files}

        files_rows = [replicate_set_timeline.generate_fit_table(files_data[f], f) for f in files_data]

        final_rows = [["metabolite", "filename", "well", "Km 1", "Km 2", "Km 3", "Km 4", "kcat 1", "kcat 2", "kcat 3",
                       "kcat 4", "kcat/Km 1", "kcat/Km 2", "kcat/Km 3", "kcat/Km 4", "R^2 1", "R^2 2", "R^2 3",
                       "R^2 4", "Km stdev/avg", "kcat stdev/avg", "kcat/Km stdev/avg", "notes"]] + \
                     [x for xs in files_rows for x in xs]

        write_output(final_rows, join(args.output, 'all_fits.csv'), mode='a')

        for f in input_files:
            for rstl in files_data[f]:
                filename_prefix = f.removesuffix('.txt')
                # TODO rstl and tl should know metabolite name (rstl will have to know their own filename for this)
                metabolite = metabolite_naming.find_metabolite(filename_prefix, rstl.well)
                if metabolite is not None:
                    metabolite = metabolite.replace('/', '-')
                    output_plot(rstl, args.output, unbundle=not args.bundle, title=metabolite)
                else:
                    output_plot(rstl, args.output, unbundle=not args.bundle, title=filename_prefix + ' ' + rstl.well)


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

        if isfile(args.output):
            # TODO get parent dir of output filename
            raise ValueError(f"Output '{args.output}' is not a directory")
        for rstl in data:
            output_plot(rstl, args.output)


if __name__ == '__main__':
    main()

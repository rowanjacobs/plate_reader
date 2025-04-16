from collections import defaultdict
from datetime import datetime

from replicate_set import ReplicateSet
from replicate_set_timeline import ReplicateSetTimeline, group_and_join_replicate_set_timelines


def time_in_seconds(time_str):
    time_format = "%H:%M:%S"
    return (datetime.strptime(time_str, time_format) - datetime(1900, 1, 1)).seconds


def float_or_overflow(x):
    return 5.0 if x == 'OVRFLW' else float(x)


def data_into_replicate_set_timelines(data_lines):
    wells_split = data_lines[0].split('\t')[2:]
    wells = []
    for i, string in enumerate(data_lines[1].split('\t')[2:]):
        if string and string != '\n':
            wells.append((i+2, wells_split[i]))

    by_col = defaultdict(list)
    for value, well in wells:
        col = int(well[1:])
        by_col[col].append((value, well))

    well_groups = []
    sorted_cols = sorted(by_col.keys())

    for i in range(0, len(sorted_cols), 2):
        c1 = by_col[sorted_cols[i]]
        try:
            c2 = by_col[sorted_cols[i + 1]]
            block = c1 + c2
        except IndexError:
            block = c1
        block_dict = {well: val for val, well in sorted(block, key=lambda x: x[1])}
        well_groups.append(block_dict)

    rstls = []
    for wg in well_groups:
        wg_rstls = []
        for well in wg.keys():
            rstl = ReplicateSetTimeline(well=well, replicate_sets=[])
            for line in data_lines[1:]:
                split = line.split('\t')
                time = time_in_seconds(split[0])
                data = float_or_overflow(split[wg[well]])
                rs = ReplicateSet(time=time, data_points=[data], well=well)
                rstl.replicate_sets.append(rs)
            wg_rstls.append(rstl)
        wg_rstl = wg_rstls[0]
        for rstl in wg_rstls[1:]:
            wg_rstl = wg_rstl.join(rstl)
        rstls.append(wg_rstl)
    return rstls


def data_into_replicate_set_timelines_single_line(data_lines):
    wells = data_lines[0].split()[3:]
    data_line_0 = data_lines[1].split('\t')
    first_well, last_well = 0, len(wells)
    started_wells = False
    for i, string in enumerate(data_line_0[2:]):
        if string:
            if not started_wells:
                first_well = i
                started_wells = True
            last_well = i
        if started_wells and not string:
            break

    replicate_set_timelines = [ReplicateSetTimeline(well=w, replicate_sets=[]) for w in
                               wells[first_well:last_well + 1]]

    for line in data_lines[1:]:
        split = line.split('\t')
        time = time_in_seconds(split[0])
        for i in range(first_well + 2, last_well + 3):
            try:
                rs = ReplicateSet(time=time, data_points=[float_or_overflow(split[i])],
                                  well=wells[i - 2])
                replicate_set_timelines[i - (first_well + 2)].replicate_sets.append(rs)
            except ValueError:
                print(f"Value error for well {wells[i - 2]}: could not parse value '{split[i]}' at position {i}")
                print("Check to see whether the following line was parsed correctly:")
                exit(ValueError)

    return replicate_set_timelines

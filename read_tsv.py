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
            for i, line in enumerate(data_lines[1:]):
                split = line.split('\t')
                try:
                    time = time_in_seconds(split[0])
                except ValueError:
                    print(f"Value error for line {i}: could not parse value '{split[0]}' as time")
                    break
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
    wells_split = data_lines[0].split('\t')[2:]
    wells = []
    for i, string in enumerate(data_lines[1].split('\t')[2:]):
        if string and string != '\n':
            wells.append((i+2, wells_split[i]))

    rstls = []
    for i, well in wells:
        rstl = ReplicateSetTimeline(well=well, replicate_sets=[])
        for line in data_lines[1:]:
            split = line.split('\t')
            time = time_in_seconds(split[0])
            data = float_or_overflow(split[i])
            rs = ReplicateSet(time=time, data_points=[data], well=well)
            rstl.replicate_sets.append(rs)
        rstls.append(rstl)
    return rstls

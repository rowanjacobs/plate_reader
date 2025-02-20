from datetime import datetime

from replicate_set import ReplicateSet
from replicate_set_timeline import ReplicateSetTimeline, group_and_join_replicate_set_timelines


def time_in_seconds(time_str):
    time_format = "%H:%M:%S"
    return (datetime.strptime(time_str, time_format) - datetime(1900, 1, 1)).seconds


def float_or_overflow(x):
    return 5.0 if x == 'OVRFLW' else float(x)


def data_into_replicate_set_timelines(data_lines):
    wells = data_lines[0].split()[3:]
    well_groups = [wells[i] + wells[i + 1] for i in range(0, len(wells), 2)]
    replicate_set_timelines_dict = {wg: ReplicateSetTimeline(well=wg, replicate_sets=[]) for wg in well_groups}
    for line in data_lines[1:]:
        split = line.split()
        time = time_in_seconds(split[0])
        # starting at index 2, read line in chunks of 2 apiece
        data_groups = [[float_or_overflow(split[i + 2]), float_or_overflow(split[i + 3])] for i in
                       range(0, len(wells), 2)]
        for i in range(0, len(well_groups)):
            rs = ReplicateSet(time=time, data_points=data_groups[i], well=well_groups[i])
            replicate_set_timelines_dict[well_groups[i]].replicate_sets.append(rs)
    rstls = sorted(replicate_set_timelines_dict.values(), key=lambda rstl: rstl.well)
    return group_and_join_replicate_set_timelines(rstls)


def data_into_replicate_set_timelines_single_line(data_lines):
    wells = data_lines[0].split()[3:]
    data_line_0 = data_lines[1].split('\t')
    first_well, last_well = 0, len(wells)
    for i, string in enumerate(data_line_0[2:]):
        if string:
            if first_well == 0:
                first_well = i
            last_well = i
        if first_well > 0 and not string:
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

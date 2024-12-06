import dataclasses

import read_tsv


@dataclasses.dataclass
class ReplicateSet:
    time: int
    data_points: list[float]
    well: str

    def join(self, rs):
        # assume that time is the same. TODO probably throw an error if it isn't
        return ReplicateSet(time=self.time, data_points=self.data_points + rs.data_points, well=self.well + rs.well)


@dataclasses.dataclass
class ReplicateSetTimeline:
    well: str
    replicate_sets: list[ReplicateSet]

    def join(self, rstl):
        # TODO check that you are joining sets with the same time
        # TODO check that sets have the same length
        joined_rs = [self.replicate_sets[i].join(rstl.replicate_sets[i]) for i in range(len(self.replicate_sets))]
        return ReplicateSetTimeline(well=self.well + rstl.well, replicate_sets=joined_rs)


def data_into_replicate_set_timelines(data_lines):
    wells = data_lines[0].split()[3:]
    well_groups = [wells[i] + wells[i + 1] for i in range(0, len(wells), 2)]
    replicate_set_timelines_dict = {wg: ReplicateSetTimeline(well=wg, replicate_sets=[]) for wg in well_groups}
    for line in data_lines[1:]:
        split = line.split()
        time = read_tsv.time_in_seconds(split[0])
        # starting at index 2, read line in chunks of 2 apiece
        data_groups = [[float(split[i + 2]), float(split[i + 3])] for i in range(0, len(wells), 2)]
        for i in range(0, len(well_groups)):
            rs = ReplicateSet(time=time, data_points=data_groups[i], well=well_groups[i])
            replicate_set_timelines_dict[well_groups[i]].replicate_sets.append(rs)
    rstls = sorted(replicate_set_timelines_dict.values(), key=lambda rstl: rstl.well)
    return group_and_join_replicate_sets(rstls)


def group_and_join_replicate_sets(data):
    """
    Groups ReplicateSetTimeline objects two by two based on their 'well' field and joins them.
    Args:
        data (list): A sorted list of ReplicateSetTimeline objects.
    Returns:
        list: A list of joined ReplicateSetTimeline objects.
    """
    if not data:
        return []

    result = []
    # Extract the first letter from the well field of the first item
    starting_letter = data[0].well[0]

    for i in range(0, len(data) - 1, 2):
        # Parse the wells
        well1 = data[i].well
        well2 = data[i + 1].well

        # Check if they belong to consecutive rows (e.g., 'YnYn+1' and 'Y+1nY+1n+1')
        if well1[0] == starting_letter and well2[0] == chr(ord(starting_letter) + 1):
            # Use the join method to combine the two ReplicateSetTimeline objects
            result.append(data[i].join(data[i + 1]))

        # Update the starting_letter to the next pair's starting row
        starting_letter = chr(ord(starting_letter) + 2)

    return result

# mock_data_lines = """Time	T∞ 340	A1	A2	A3	A4	B1	B2	B3	B4
# 0:00:00	25.0	1.691	1.736	1.787	1.837	2.069	2.065	1.907	1.480
# 0:00:12	25.0    1.791	1.836	1.887	1.937	2.169	2.165	2.007	1.580
# """
#
# mock_data_replicate_sets = [
#     ReplicateSetTimeline('A1A2B1B2', [
#         ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065]),
#         ReplicateSet(time=12, well='A1A2B1B2', data_points=[1.791, 1.836, 2.169, 2.165])
#     ]),
#     ReplicateSetTimeline('A3A4B3B4', [
#         ReplicateSet(time=0, well='A3A4B3B4', data_points=[1.787, 1.837, 1.907, 1.480]),
#         ReplicateSet(time=12, well='A3A4B3B4', data_points=[1.887, 1.937, 2.007, 1.580])
#     ])
# ]

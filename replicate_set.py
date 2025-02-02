import dataclasses
import statistics

import apply_statistics
import read_tsv

# ε₃₄₀(NADH) = 6220 M⁻¹cm⁻¹
# A = εlc

path_length = 0.195565054
extinction = 6220


@dataclasses.dataclass
class ReplicateSet:
    time: int
    data_points: list[float]
    well: str

    def join(self, rs):
        # assume that time is the same. TODO probably throw an error if it isn't
        return ReplicateSet(time=self.time, data_points=self.data_points + rs.data_points, well=self.well + rs.well)

    def concentrations(self):
        return [x / (path_length * extinction) for x in self.data_points]

    def _concentrations_without_outliers(self):
        concs = self.concentrations()
        if len(concs) < 3:
            return concs
        outlier, _ = apply_statistics.grubbs_test(concs)
        if outlier > -1:
            del concs[outlier]
        return concs

    def mean_concentration(self):
        return statistics.mean(self._concentrations_without_outliers())

    def stdev_concentration(self):
        if len(self.concentrations()) < 2:
            return 0
        return statistics.stdev(self._concentrations_without_outliers())


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
        time = read_tsv.time_in_seconds(split[0])
        for i in range(first_well + 2, last_well + 3):
            try:
                rs = ReplicateSet(time=time, data_points=[5.0 if split[i] == 'OVRFLW' else float(split[i])],
                                  well=wells[i - 2])
                replicate_set_timelines[i - (first_well + 2)].replicate_sets.append(rs)
            except ValueError:
                print(f"Value error for well {wells[i - 2]}: could not parse value '{split[i]}' at position {i}")
                print("Check to see whether the following line was parsed correctly:")
                exit(ValueError)

    return replicate_set_timelines


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


def generate_timeline_table(rstls):
    # Extract all unique times and wells maintaining original order
    times = sorted(set(rs.time for rstl in rstls for rs in rstl.replicate_sets))
    wells = []
    seen_wells = set()
    for rstl in rstls:
        for rs in rstl.replicate_sets:
            if rs.well not in seen_wells:
                wells.append(rs.well)
                seen_wells.add(rs.well)

    # Initialize the table with column headers
    table = [["Time"] + wells]

    # Populate the rows
    for time in times:
        row = [time]
        for well in wells:
            # Find the corresponding ReplicateSet for the given time and well
            concentration_values = None
            for rstl in rstls:
                for rs in rstl.replicate_sets:
                    if rs.time == time and rs.well == well:
                        concentration_values = rs.mean_concentration()
                        break
                if concentration_values:
                    break
            row.append(concentration_values if concentration_values else [])
        table.append(row)

    return table

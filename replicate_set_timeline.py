import dataclasses
from typing import List

from kinetics_modeling import fit
from replicate_set import ReplicateSet


@dataclasses.dataclass
class ReplicateSetTimeline:
    well: str
    replicate_sets: list[ReplicateSet]

    def join(self, rstl):
        # TODO check that you are joining sets with the same time
        # TODO check that sets have the same length
        joined_rs = [self.replicate_sets[i].join(rstl.replicate_sets[i]) for i in range(len(self.replicate_sets))]
        return ReplicateSetTimeline(well=self.well + rstl.well, replicate_sets=joined_rs)

    def fit(self):
        data = [rs.mean_concentration() for rs in self.replicate_sets]
        times = [rs.time for rs in self.replicate_sets]
        result = fit(times, data)
        # TODO check success status
        # TODO write tests
        return result.params


def group_and_join_replicate_set_timelines(data):
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


def generate_fit_table(rstls: List[ReplicateSetTimeline]):
    fits = {}
    for rstl in rstls:
        # TODO catch errors in fitting
        params = rstl.fit()
        fits[rstl.well] = params

    fits_sorted = sorted(list(fits.keys()))

    table = [["well", "Km", "kcat"]]
    for well in fits_sorted:
        params = fits[well]
        k_m = params['k_m'].value.item()
        v_max = params['k_cat'].value.item()
        table.append([well, k_m, v_max])

    return table


def generate_timeline_table(rstls):
    # Extract all unique times and wells maintaining original order
    times = sorted(set(rs.time for rstl in rstls for rs in rstl.replicate_sets))
    wells = sorted(set(rs.well for rstl in rstls for rs in rstl.replicate_sets))

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

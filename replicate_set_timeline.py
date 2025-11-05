import dataclasses
from typing import List

import metabolite_naming
from kinetics_modeling import fit, approx_lambert_w, e0
from replicate_set import ReplicateSet

import matplotlib.pyplot as plt


@dataclasses.dataclass
class ReplicateSetTimeline:
    well: str
    replicate_sets: list[ReplicateSet]
    k_m = 0
    k_cat = 0
    __has_fit = False

    def join(self, rstl):
        # TODO check that you are joining sets with the same time
        # TODO check that sets have the same length
        joined_rs = [self.replicate_sets[i].join(rstl.replicate_sets[i]) for i in range(len(self.replicate_sets))]
        return ReplicateSetTimeline(well=self.well + rstl.well, replicate_sets=joined_rs)

    def fit(self):
        if self.__has_fit:
            return {'k_m': self.k_m, 'k_cat': self.k_cat}

        data = [rs.mean_concentration() for rs in self.replicate_sets]
        times = [rs.time for rs in self.replicate_sets]
        result = fit(times, data)
        # TODO check success status
        # TODO write tests
        self.k_m = result.params['k_m'].value.item()
        self.k_cat = result.params['k_cat'].value.item()
        self.__has_fit = True

        return result.params

    def plot_data(self):
        data = [rs.mean_concentration() for rs in self.replicate_sets]
        times = [rs.time for rs in self.replicate_sets]
        return times, data

    def plot(self, title_override=None):
        fig, ax = plt.subplots()
        x, y = self.plot_data()
        ax.plot(x, y, '.:b')

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('[NADH] (M)')
        if title_override:
            title = title_override
        else:
            title = self.well
        ax.set_title(title)

        self.fit()
        k_m = self.k_m
        k_cat = self.k_cat
        v_max = k_cat * e0
        s0 = max(y) - min(y)
        s_min = min(y)

        ax.text(300, max(y)*.9, f'$K_m={k_m:.3e},\\ k_{{cat}}={k_cat:.3f}$')

        y2 = [s_min + k_m * approx_lambert_w(s0, k_m, v_max, t) for t in x]
        ax.plot(x, y2, 'g')

        return fig

    def normalize(self):
        raw_data = [s for rs in self.replicate_sets for s in rs.data_points]
        s0 = min(raw_data)
        for rs in self.replicate_sets:
            rs.data_points = [s - s0 for s in rs.data_points]


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


def generate_fit_table(rstls: List[ReplicateSetTimeline], filename=''):
    fits = {}
    for rstl in rstls:
        # TODO catch errors in fitting
        params = rstl.fit()
        fits[rstl.well] = params

    fits_sorted = sorted(list(fits.keys()))

    table = []
    for well in fits_sorted:
        params = fits[well]
        k_m = params['k_m'].value.item()
        k_cat = params['k_cat'].value.item()
        if filename != '':
            metabolite = metabolite_naming.find_metabolite(filename, well)
            table.append([metabolite, filename, well, k_m, k_cat, k_cat / k_m])
        else:
            table.append([well, k_m, k_cat, k_cat / k_m])

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

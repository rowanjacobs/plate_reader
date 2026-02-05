import copy
import dataclasses
import math
import warnings
from statistics import mean
from typing import List

import numpy
from lmfit import Model

import metabolite_naming
from absorbance import path_length, extinction
from kinetics_modeling import fit, approx_lambert_w, e0
from replicate_set import ReplicateSet

import matplotlib.pyplot as plt


@dataclasses.dataclass
class ReplicateSetTimeline:
    well: str
    replicate_sets: list[ReplicateSet]
    # TODO it's getting to the point that you want to refactor timelines out as a dataclass or something
    timelines: dict[str, list[float]] = dataclasses.field(default_factory=dict)
    timeline_r_squared: dict[str, float] = dataclasses.field(default_factory=dict)
    fits: dict[str, dict[str, float]] = dataclasses.field(default_factory=dict)
    k_m = 0
    k_cat = 0
    fit_results: dict[str, Model] = dataclasses.field(default_factory=dict)
    __has_fit = False

    def join(self, rstl):
        # TODO check that you are joining sets with the same time
        # TODO check that sets have the same length
        joined_rs = [self.replicate_sets[i].join(rstl.replicate_sets[i]) for i in range(len(self.replicate_sets))]
        return ReplicateSetTimeline(well=self.well + rstl.well, replicate_sets=joined_rs)

    def fit(self):
        self.bundle()

        if self.__has_fit:
            return self.fits

        times = [rs.time for rs in self.replicate_sets]
        timelines_data = {k: [x / (path_length * extinction) for x in v] for k, v in self.timelines.items()}
        for well in self.timelines.keys():
            result = fit(times, timelines_data[well])
            # TODO check success status
            # TODO write tests
            self.fit_results[well] = result
            self.fits[well] = {'k_m': result.params['k_m'].value.item(), 'k_cat': result.params['k_cat'].value.item()}
            self.timeline_r_squared[well] = 1 - result.residual.var() / numpy.var(self.timelines[well])
            # TODO add the other statistics too
        self.__has_fit = True

        self.k_m = mean([self.fits[well]['k_m'] for well in self.timelines.keys()])
        self.k_cat = mean([self.fits[well]['k_cat'] for well in self.timelines.keys()])

        return self.fits

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
        s0 = max(y)
        s_min = min(y)  # should always be 0.0

        ax.text(300, max(y) * .9, f'$K_m={k_m:.3e},\\ k_{{cat}}={k_cat:.3f}$')

        y2 = [s_min + k_m * approx_lambert_w(s0, k_m, v_max, t) for t in x]
        ax.plot(x, y2, 'g')

        return fig

    def bundle_plot_data(self):
        self.bundle()
        data = {k: list(map(lambda y: y / (path_length * extinction), v)) for k, v in self.timelines.items()}
        times = [rs.time for rs in self.replicate_sets]
        return times, data

    def bundle_plot(self, title_override=None):
        colors = ['b', 'r', 'm', 'c', 'y']
        colormap = {}
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('[NADH] (M)')
        if title_override:
            title = title_override
        else:
            title = self.well
        ax.set_title(title)

        x, ys = self.bundle_plot_data()
        for i, (k, v) in enumerate(ys.items()):
            colormap[k] = colors[i]
            ax.plot(x, v, '.:' + colors[i])

        max_y = max([v[0] for _, v in ys.items()])
        self.fit()

        fit_colors = iter(['g', "tab:gray", "tab:brown", "tab:orange"])
        for i, k in enumerate(self.timelines.keys()):
            k_m = self.fits[k]['k_m']
            k_cat = self.fits[k]['k_cat']
            v_max = k_cat * e0
            s0 = max(ys[k])
            s_min = min(ys[k])  # should always be 0
            r_squared = self.timeline_r_squared[k]

            color = next(fit_colors)
            ax.text(300, max_y * (.7 + i * 0.1), f'$K_m={k_m:.3e},\\ k_{{cat}}={k_cat:.3f}$', color=color)
            ax.text(300, max_y * (.3 + i * 0.1), f'$R^2={r_squared}$', color=color)

            y2 = [s_min + k_m * approx_lambert_w(s0, k_m, v_max, t) for t in x]
            ax.plot(x, y2, color)

        return fig

    def bundle(self):
        if len(self.timelines.items()) > 0:
            return

        wells = {k for rs in self.replicate_sets for k, _ in rs.data_points.items()}
        timelines = {k: [] for k in wells}

        for well in wells:
            for rs in self.replicate_sets:
                try:
                    timelines[well].append(rs.data_points[well])
                except KeyError:
                    continue

        self.timelines = timelines


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


def pad(array):
    if len(array) >= 4:
        return array

    if len(array) == 3:
        return array + ['']

    return pad(array + [''])


def generate_fit_table(rstls: List[ReplicateSetTimeline], filename=''):
    fits = {}
    r_squareds = {}
    for rstl in rstls:
        # TODO catch errors in fitting
        # this is in a format like {'A1': {'k_m': 1E-5, 'k_cat': 2.5}}
        params = rstl.fit()
        fits[rstl.well] = params
        wells = sorted(list(rstl.timeline_r_squared))
        r_squareds[rstl.well] = [rstl.timeline_r_squared[x] for x in wells]

    fits_sorted = sorted(list(fits.keys()))

    table = []
    for well in fits_sorted:
        params = fits[well]
        k_m = pad([params[k]['k_m'] for k in sorted(params.keys())])
        k_cat = pad([params[k]['k_cat'] for k in sorted(params.keys())])
        k_cat_over_k_m = pad([params[k]['k_cat']/params[k]['k_m'] for k in sorted(params.keys())])
        r_squared = pad(r_squareds[well])
        if filename != '':
            metabolite = metabolite_naming.find_metabolite(filename, well)
            table.append([metabolite, filename, well] + k_m + k_cat + k_cat_over_k_m + r_squared)
        else:
            table.append([filename, well] + k_m + k_cat + k_cat_over_k_m + r_squared)

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

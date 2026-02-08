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

from timeline import Timeline


@dataclasses.dataclass
class ReplicateSetTimeline:
    well: str
    replicate_sets: list[ReplicateSet]
    timelines: dict[str, Timeline] = dataclasses.field(default_factory=dict)
    k_m = 0.0
    k_cat = 0.0
    __has_fit = False

    def join(self, rstl):
        # TODO check that you are joining sets with the same time
        # TODO check that sets have the same length
        joined_rs = [self.replicate_sets[i].join(rstl.replicate_sets[i]) for i in range(len(self.replicate_sets))]
        return ReplicateSetTimeline(well=self.well + rstl.well, replicate_sets=joined_rs)

    def fit(self):
        self.bundle()

        if self.__has_fit:
            return {k: v.fit for k, v in self.timelines.items()}

        times = [rs.time for rs in self.replicate_sets]
        timelines_data = {k: v.concentrations() for k, v in self.timelines.items()}
        for well in self.timelines.keys():
            result = fit(times, timelines_data[well])
            # TODO check success status
            # TODO write tests
            self.timelines[well].fit_result = result
            k_m = result.params['k_m'].value.item()
            try:
                k_cat = result.params['k_cat'].value.item()
            except AttributeError:
                k_cat = 1e-100  # that's the k_cat value in fit results that trigger this error
            self.timelines[well].fit = {'k_m': k_m, 'k_cat': k_cat}
            self.timelines[well].k_m = k_m
            self.timelines[well].k_cat = k_cat
            self.timelines[well].r_squared = 1 - result.residual.var() / numpy.var(timelines_data[well])
        self.__has_fit = True

        self.k_m = mean([self.timelines[well].k_m for well in self.timelines.keys()])
        self.k_cat = mean([self.timelines[well].k_cat for well in self.timelines.keys()])

        return {k: v.fit for k, v in self.timelines.items()}

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
        times = [rs.time for rs in self.replicate_sets]
        return times, {k: tl.concentrations() for k, tl in self.timelines.items() if not tl.reject()}

    def bundle_plot(self, title_override=None):
        colors = ['b', 'r', 'm', 'c', 'y']
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('[NADH] (M)')
        if title_override:
            title = title_override
        else:
            title = self.well
        ax.set_title(title)

        x, ys = self.bundle_plot_data()

        s0s = [v[0] for _, v in ys.items()]
        if len(s0s) == 0:
            return fig

        max_y = max(s0s)
        self.fit()

        fit_colors = iter(['g', "tab:gray", "tab:brown", "tab:orange"])
        for i, (k, tl) in enumerate([(k, tl) for k, tl in self.timelines.items() if not tl.reject()]):
            ax.plot(x, tl.concentrations(), '.:' + colors[i])

            k_m = tl.k_m
            k_cat = tl.k_cat
            v_max = k_cat * e0
            s0 = max(ys[k])
            s_min = min(ys[k])  # should always be 0
            r_squared = tl.r_squared

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
            tl = Timeline(well)
            for rs in self.replicate_sets:
                try:
                    tl.absorbances.append(rs.data_points[well])
                except KeyError:
                    continue
            timelines[well] = tl

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
    timelines = {}
    # fits = {}
    for rstl in rstls:
        # this is in a format like {'A1': {'k_m': 1E-5, 'k_cat': 2.5}}
        # params = rstl.fit()
        # fits[rstl.well] = params
        rstl.fit()
        timelines[rstl.well] = rstl.timelines

    well_groups = sorted(list(timelines.keys()))

    table = []
    for well_group in well_groups:
        tls = timelines[well_group]
        wells = sorted(tls.keys())
        k_m = pad([tls[k].k_m_output() for k in wells])
        k_cat = pad([tls[k].k_cat_output() for k in wells])
        k_cat_over_k_m = pad([tls[k].k_cat_over_k_m() for k in wells])
        r_squared = pad([tls[k].r_squared_output() for k in wells])

        notes = '; '.join([f'rejected {tl.well} with R²={tl.r_squared}' for tl in tls.values() if tl.reject()])
        # TODO put notes and rejections here
        if filename != '':
            metabolite = metabolite_naming.find_metabolite(filename, well_group)
            table.append([metabolite, filename, well_group] + k_m + k_cat + k_cat_over_k_m + r_squared + [notes])
        else:
            table.append([filename, well_group] + k_m + k_cat + k_cat_over_k_m + r_squared + [notes])

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

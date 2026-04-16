import os
from os.path import join

import matplotlib
from matplotlib import pyplot as plt

from one_off_plot_data import hit, wtgs, hit_name
from replicate_set_timeline import ReplicateSetTimeline
from timeline import Timeline


class MergedReplicateSetTimeline(ReplicateSetTimeline):
    def get_times(self):
        return list(range(0, 612, 12))

    @staticmethod
    def fit_colors():
        fit_colors = ['xkcd:green', 'xkcd:teal', 'xkcd:black', 'xkcd:forest', 'xkcd:amethyst',
                      'xkcd:cherry red', 'xkcd:bubblegum pink', 'xkcd:adobe']
        # fit_colors = list(matplotlib.colors.TABLEAU_COLORS.keys()) + list(matplotlib.colors.BASE_COLORS.keys())
        return fit_colors

    @staticmethod
    def get_colors():
        point_colors = ['xkcd:lime green', 'xkcd:cyan', 'xkcd:black', 'xkcd:jungle green', 'xkcd:deep violet',
                        'xkcd:faded red', 'xkcd:barbie pink', 'xkcd:mud brown']
        # colors = list(matplotlib.colors.XKCD_COLORS.keys())
        return point_colors

    @staticmethod
    def plot_legend(ax, color, i, k_cat, k_m, max_y, r_squared):
        pass


def main():
    merged_rstl = MergedReplicateSetTimeline('all data', [])

    for i, array in enumerate(hit):
        name = hit_name + ' ' + str(i)
        hit_tl = Timeline(name)
        hit_tl.absorbances = array
        merged_rstl.timelines[name] = hit_tl

    for i, array in enumerate(wtgs):
        name = 'wild-type glutamine synthetase ' + str(i)
        wtgs_tl = Timeline(name)
        wtgs_tl.absorbances = array
        merged_rstl.timelines[name] = wtgs_tl

    print(merged_rstl.fit())

    title = hit_name + " compared to wild-type GS"
    fig = merged_rstl.bundle_plot(title_override=title)
    fig.savefig(join(os.getcwd(), title + '.png'))
    plt.close(fig)


if __name__ == '__main__':
    main()

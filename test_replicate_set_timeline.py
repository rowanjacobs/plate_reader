import dataclasses
import unittest

import custom_matchers
import helpers
from replicate_set import ReplicateSet
from replicate_set_timeline import ReplicateSetTimeline


class TestReplicateSetTimeline(unittest.TestCase):
    rstl1 = ReplicateSetTimeline(
        well='A1A2',
        replicate_sets=[
            ReplicateSet(time=0, data_points={'A1': 0.123, 'A2': 0.345}),
            ReplicateSet(time=6, data_points={'A1': 1.123, 'A2': 1.345}),
            ReplicateSet(time=12, data_points={'A1': 2.123, 'A2': 2.345})
        ]
    )

    def test_plot_data(self):
        expected_data = ([0, 6, 12], [
            helpers.average_and_apply_beers_law([0.123, 0.345]),
            helpers.average_and_apply_beers_law([1.123, 1.345]),
            helpers.average_and_apply_beers_law([2.123, 2.345])
        ])

        custom_matchers.assert_arrays_of_arrays_almost_equal(self, self.rstl1.plot_data(), expected_data)

    def test_normalize(self):
        rstl_expected = ReplicateSetTimeline(
            well='A1A2',
            replicate_sets=[
                ReplicateSet(time=0, data_points={'A1': 0.0, 'A2': 0.222}),
                ReplicateSet(time=6, data_points={'A1': 1.0, 'A2': 1.222}),
                ReplicateSet(time=12, data_points={'A1': 2.0, 'A2': 2.222})
            ]
        )
        rstl = dataclasses.replace(self.rstl1)
        rstl.normalize()
        custom_matchers.assert_replicate_set_timelines_almost_equal(self, rstl, rstl_expected)

    def test_bundle_timelines(self):
        # TODO fix data model and return here
        pass

    def test_join_replicate_set_timelines(self):
        rstl2 = ReplicateSetTimeline(
            well='B1B2',
            replicate_sets=[
                ReplicateSet(time=0, data_points={'B1': 0.678, 'B2': 0.901}),
                ReplicateSet(time=6, data_points={'B1': 1.678, 'B2': 1.901}),
                ReplicateSet(time=12, data_points={'B1': 2.678, 'B2': 2.901})
            ]
        )
        rstl_expected = ReplicateSetTimeline(
            well='A1A2B1B2',
            replicate_sets=[
                ReplicateSet(time=0, data_points={'A1': 0.123, 'A2': 0.345, 'B1': 0.678, 'B2': 0.901}),
                ReplicateSet(time=6, data_points={'A1': 1.123, 'A2': 1.345, 'B1': 1.678, 'B2': 1.901}),
                ReplicateSet(time=12, data_points={'A1': 2.123, 'A2': 2.345, 'B1': 2.678, 'B2': 2.901})
            ]
        )
        custom_matchers.assert_replicate_set_timelines_almost_equal(self, self.rstl1.join(rstl2), rstl_expected)

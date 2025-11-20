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

    def test_bundle_plot_data(self):
        expected_data = ([0, 6, 12], {
            'A1': helpers.apply_beers_law([0.123, 1.123, 2.123]),
            'A2': helpers.apply_beers_law([0.345, 1.345, 2.345]),
        })

        custom_matchers.assert_dicts_with_float_arrays_almost_equal(self, self.rstl1.bundle_plot_data()[1],
                                                                    expected_data[1])

    def test_bundle_fit(self):
        self.rstl1.bundle_fit()

        self.assertSetEqual(set(self.rstl1.bundle_k_m.keys()), {'A1', 'A2'})
        self.assertSetEqual(set(self.rstl1.bundle_k_cat.keys()), {'A1', 'A2'})

        custom_matchers.assert_dicts_with_floats_almost_equal(self, self.rstl1.bundle_k_cat,
                                                              {'A1': 18424.833830796146, 'A2': 18424.83604383564})
        custom_matchers.assert_dicts_with_floats_almost_equal(self, self.rstl1.bundle_k_m,
                                                              {'A1': 1.0271789884694902, 'A2': 1.0271791119747518})

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

    def test_bundle(self):
        self.rstl1.bundle()

        custom_matchers.assert_dicts_with_float_arrays_almost_equal(self, self.rstl1.timelines,
                                                                    {'A1': [0.123, 1.123, 2.123],
                                                                     'A2': [0.345, 1.345, 2.345]})

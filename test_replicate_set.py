import unittest

import helpers
from replicate_set import ReplicateSet, ReplicateSetTimeline, data_into_replicate_set_timelines


class TestReplicateSet(unittest.TestCase):
    def test_join_replicate_sets(self):
        rs1 = ReplicateSet(time=0, data_points=[0.123, 0.345], well='A1A2')
        rs2 = ReplicateSet(time=0, data_points=[0.678, 0.901], well='B1B2')
        rs_expected = ReplicateSet(time=0, data_points=[0.123, 0.345, 0.678, 0.901], well='A1A2B1B2')
        helpers.assert_replicate_sets_almost_equal(self, rs_expected, rs1.join(rs2))

    def test_replicate_set_beers_law(self):
        rs = ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065])
        concentrations = rs.concentrations()
        concs_expected = [1.691 / (0.195565054 * 6220), 1.736 / (0.195565054 * 6220), 2.069 / (0.195565054 * 6220),
                          2.065 / (0.195565054 * 6220)]
        helpers.assert_arrays_almost_equal(self, concs_expected, concentrations)

    def test_replicate_set_mean_concentrations(self):
        rs = ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065])
        helpers.assert_almost_equal(self, 0.001553952035962246, rs.mean_concentration())

    def test_replicate_set_mean_concentrations_excludes_outliers(self):
        rs = ReplicateSet(time=0, well='A3A4B3B4', data_points=[1.787, 1.837, 1.907, 1.480])
        # mean of concentration for first 3 points only
        helpers.assert_almost_equal(self, 0.0015156564318489058, rs.mean_concentration())

    def test_join_replicate_set_timelines(self):
        rstl1 = ReplicateSetTimeline(
            well='A1A2',
            replicate_sets=[
                ReplicateSet(time=0, data_points=[0.123, 0.345], well='A1A2'),
                ReplicateSet(time=6, data_points=[1.123, 1.345], well='A1A2'),
                ReplicateSet(time=12, data_points=[2.123, 2.345], well='A1A2')
            ]
        )
        rstl2 = ReplicateSetTimeline(
            well='B1B2',
            replicate_sets=[
                ReplicateSet(time=0, data_points=[0.678, 0.901], well='B1B2'),
                ReplicateSet(time=6, data_points=[1.678, 1.901], well='B1B2'),
                ReplicateSet(time=12, data_points=[2.678, 2.901], well='B1B2')
            ]
        )
        rstl_expected = ReplicateSetTimeline(
            well='A1A2B1B2',
            replicate_sets=[
                ReplicateSet(time=0, data_points=[0.123, 0.345, 0.678, 0.901], well='A1A2B1B2'),
                ReplicateSet(time=6, data_points=[1.123, 1.345, 1.678, 1.901], well='A1A2B1B2'),
                ReplicateSet(time=12, data_points=[2.123, 2.345, 2.678, 2.901], well='A1A2B1B2')
            ]
        )
        helpers.assert_replicate_set_timelines_almost_equal(self, rstl1.join(rstl2), rstl_expected)

    def test_data_into_replicate_set_timelines_parses_data(self):
        rstls = data_into_replicate_set_timelines(helpers.mock_data_lines.splitlines())
        for i, rstl in enumerate(rstls):
            helpers.assert_replicate_set_timelines_almost_equal(self, helpers.mock_data_replicate_sets[i], rstl)


if __name__ == '__main__':
    unittest.main()

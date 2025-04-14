import unittest

import custom_matchers
import helpers
from replicate_set import ReplicateSet


class TestReplicateSet(unittest.TestCase):
    def test_join_replicate_sets(self):
        rs1 = ReplicateSet(time=0, data_points=[0.123, 0.345], well='A1A2')
        rs2 = ReplicateSet(time=0, data_points=[0.678, 0.901], well='B1B2')
        rs_expected = ReplicateSet(time=0, data_points=[0.123, 0.345, 0.678, 0.901], well='A1A2B1B2')
        custom_matchers.assert_replicate_sets_almost_equal(self, rs_expected, rs1.join(rs2))

    def test_replicate_set_beers_law(self):
        rs = ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065])
        concentrations = rs.concentrations()
        concs_expected = [1.691 / (0.195565054 * 6220), 1.736 / (0.195565054 * 6220), 2.069 / (0.195565054 * 6220),
                          2.065 / (0.195565054 * 6220)]
        custom_matchers.assert_arrays_almost_equal(self, concs_expected, concentrations)

    def test_replicate_set_mean_concentrations(self):
        rs = ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065])
        custom_matchers.assert_almost_equal(self, 0.001553952035962246, rs.mean_concentration())

    def test_replicate_set_mean_concentrations_excludes_outliers(self):
        rs = ReplicateSet(time=0, well='A3A4B3B4', data_points=[1.787, 1.837, 1.907, 1.480])
        # mean of concentration for first 3 points only
        custom_matchers.assert_almost_equal(self, 0.0015156564318489058, rs.mean_concentration())

    def test_replicate_set_stdev_concentrations(self):
        rs = ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065])
        custom_matchers.assert_almost_equal(self, 0.0001684663931449787, rs.stdev_concentration())

    def test_replicate_set_stdev_concentrations_excludes_outliers(self):
        rs = ReplicateSet(time=0, well='A3A4B3B4', data_points=[1.787, 1.837, 1.907, 1.480])
        # stdev of concentration for first 3 points only
        custom_matchers.assert_almost_equal(self, 4.9553117790144295e-05, rs.stdev_concentration())


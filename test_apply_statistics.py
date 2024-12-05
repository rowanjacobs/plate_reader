import unittest

import apply_statistics
import helpers


class TestApplyStatistics(unittest.TestCase):
    def test_get_mean_concentrations(self):
        means = apply_statistics.mean_concentrations(helpers.mock_data_concentration)
        helpers.assert_arrays_almost_equal(self, helpers.mock_concentration_means, means)

    def test_get_stdev_concentrations(self):
        stdevs = apply_statistics.stdev_concentrations(helpers.mock_data_concentration)
        helpers.assert_arrays_almost_equal(self, helpers.mock_concentration_stdevs, stdevs)


if __name__ == '__main__':
    unittest.main()

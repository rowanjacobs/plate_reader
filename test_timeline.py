import unittest

import custom_matchers
from timeline import Timeline


class TestTimeline(unittest.TestCase):
    def test_concentrations(self):
        tl = Timeline('A1')
        tl.absorbances = [1.691, 1.736, 2.069, 2.065]
        concs_expected = [1.691 / (0.195565054 * 6220), 1.736 / (0.195565054 * 6220), 2.069 / (0.195565054 * 6220),
                          2.065 / (0.195565054 * 6220)]
        custom_matchers.assert_arrays_almost_equal(self, concs_expected, tl.concentrations())

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

    def test_rejected(self):
        tl = Timeline('A1')
        tl.r_squared = 0.8999999

        self.assertTrue(tl.reject())

        tl.r_squared = 0.9
        self.assertFalse(tl.reject())

    def test_k_m_output(self):
        tl = Timeline('A1')
        tl.r_squared = 0.8999999
        tl.k_m = 1E-5

        self.assertEqual('', tl.k_m_output())

        tl.r_squared = 1.0

        custom_matchers.assert_almost_equal(self, 1E-5, tl.k_m_output())

    def test_k_cat_output(self):
        tl = Timeline('A1')
        tl.r_squared = 0.8999999
        tl.k_cat = 1.5

        self.assertEqual('', tl.k_cat_output())

        tl.r_squared = 1.0

        custom_matchers.assert_almost_equal(self, 1.5, tl.k_cat_output())

    def test_k_cat_over_k_m(self):
        tl = Timeline('A1')
        tl.r_squared = 0.8999999
        tl.k_cat = 1.5
        tl.k_m = 1E-5

        self.assertEqual('', tl.k_cat_over_k_m())

        tl.r_squared = 1.0

        custom_matchers.assert_almost_equal(self, 1.5E5, tl.k_cat_over_k_m())

    def test_r_squared_output(self):
        tl = Timeline('A1')
        tl.r_squared = 0.8999999

        self.assertEqual('', tl.r_squared_output())

        tl.r_squared = 1.0

        custom_matchers.assert_almost_equal(self, 1.0, tl.r_squared_output())


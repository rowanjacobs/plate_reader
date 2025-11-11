import unittest

import custom_matchers
import helpers
from read_tsv import data_into_replicate_set_timelines, data_into_replicate_set_timelines_single_line


class TestReadTsv(unittest.TestCase):
    def test_data_into_replicate_set_timelines_parses_data(self):
        rstls = data_into_replicate_set_timelines(helpers.mock_data_lines.splitlines())
        for i, rstl in enumerate(rstls):
            custom_matchers.assert_replicate_set_timelines_almost_equal(self, helpers.mock_data_replicate_sets[i], rstl)

    def test_data_into_replicate_set_timelines_handles_overflow(self):
        data_into_replicate_set_timelines(helpers.mock_overflow_lines.splitlines())

    def test_data_into_replicate_set_timelines_handles_discontinuous_wells(self):
        rstls = data_into_replicate_set_timelines(helpers.mock_discontinuous_lines.splitlines())
        self.assertEqual('A3A4B3B4', rstls[0].well)
        custom_matchers.assert_dicts_with_floats_almost_equal(self,
                                                              {'A3': 1.498 - 1.29, 'A4': 1.705 - 1.29,
                                                               'B3': 1.32 - 1.29, 'B4': 1.919 - 1.29},
                                                              rstls[0].replicate_sets[0].data_points)

    def test_data_into_replicate_set_timelines_tries_to_group_odd_numbers_of_wells(self):
        rstls = data_into_replicate_set_timelines(helpers.mock_odd_number_rows_lines.splitlines())
        self.assertEqual('C3C4D3D4', rstls[0].well)
        self.assertEqual('C21D21', rstls[-1].well)

    def test_data_into_replicate_set_timelines_single_line_of_384_wells_detects_wells_in_use(self):
        rstls = data_into_replicate_set_timelines_single_line(helpers.mock_long_data_lines.splitlines())
        wells = [rstl.well for rstl in rstls]
        self.assertEqual(wells,
                         ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14',
                          'E15', 'E16', 'E17', 'E18', 'E19', 'E20', 'E21', 'E22', 'E23', 'E24']
                         )

    def test_data_into_replicate_set_timelines_single_line(self):
        rstls = data_into_replicate_set_timelines_single_line(helpers.mock_long_data_single_lines.splitlines())
        self.assertEqual(rstls[0].well, 'A1')

    def test_data_into_replicate_set_timelines_single_line_omits_statistical_tests(self):
        rstls = data_into_replicate_set_timelines_single_line(helpers.mock_long_data_lines.splitlines())
        rstls[0].replicate_sets[0].mean_concentration()
        rstls[0].replicate_sets[0].stdev_concentration()


if __name__ == '__main__':
    unittest.main()

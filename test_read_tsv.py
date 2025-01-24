import unittest

import helpers
from read_tsv import read_data, read_statistics


class TestReadTsv(unittest.TestCase):
    def test_read_data_returns_numeric_data(self):
        parsed_tsv = read_data(helpers.mock_data_lines.splitlines())
        helpers.assert_arrays_of_arrays_almost_equal(self, helpers.mock_data, parsed_tsv)

    def test_read_data_parses_overflow(self):
        parsed_tsv = read_data(helpers.mock_overflow_lines.splitlines())
        helpers.assert_arrays_of_arrays_almost_equal(self, helpers.mock_data_overflow, parsed_tsv)

    def test_read_statistics_returns_numeric_statistics(self):
        parsed_statistics = read_statistics(helpers.mock_statistics_lines.splitlines())
        helpers.assert_dicts_with_float_arrays_almost_equal(self, helpers.mock_statistics, parsed_statistics)


if __name__ == '__main__':
    unittest.main()

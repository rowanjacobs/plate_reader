import unittest

from trim_plate_reader_output import trim_plate_reader_output
from helpers import mock_pr_output, mock_data_lines, mock_statistics_lines


class TestTrimPlateReaderOutput(unittest.TestCase):
    def test_tpro_returns_data(self):
        tpro_output, _ = trim_plate_reader_output(mock_pr_output.splitlines())
        self.assertEqual(mock_data_lines.splitlines(), tpro_output)

    def test_tpro_returns_stats(self):
        _, tpro_stats = trim_plate_reader_output(mock_pr_output.splitlines())
        self.assertEqual(mock_statistics_lines.splitlines(), tpro_stats)


if __name__ == '__main__':
    unittest.main()

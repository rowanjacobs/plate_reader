import unittest

from metabolite_naming import find_metabolite


class TestMetaboliteNaming(unittest.TestCase):
    def test_metabolite_naming(self):
        filename = '20250611 plate 8 ROW E'
        well = 'I11I12J11J12'
        self.assertEqual('Sarcosine', find_metabolite(filename, well))

    def test_metabolite_naming_single_well(self):
        filename = '20250611 plate 8 ROW G'
        well = 'N15'
        self.assertEqual('N-Methylsarcosine', find_metabolite(filename, well))

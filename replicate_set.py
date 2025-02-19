import dataclasses
import statistics

import outliers

# ε₃₄₀(NADH) = 6220 M⁻¹cm⁻¹
# A = εlc

path_length = 0.195565054
extinction = 6220


@dataclasses.dataclass
class ReplicateSet:
    time: int
    data_points: list[float]
    well: str

    def join(self, rs):
        # assume that time is the same. TODO probably throw an error if it isn't
        return ReplicateSet(time=self.time, data_points=self.data_points + rs.data_points, well=self.well + rs.well)

    def concentrations(self):
        return [x / (path_length * extinction) for x in self.data_points]

    def _concentrations_without_outliers(self):
        concs = self.concentrations()
        if len(concs) < 3:
            return concs
        outlier, _ = outliers.grubbs_test(concs)
        if outlier > -1:
            del concs[outlier]
        return concs

    def mean_concentration(self):
        return statistics.mean(self._concentrations_without_outliers())

    def stdev_concentration(self):
        if len(self.concentrations()) < 2:
            return 0
        return statistics.stdev(self._concentrations_without_outliers())


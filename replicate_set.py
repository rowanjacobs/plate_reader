import dataclasses
import statistics

from absorbance import path_length, extinction


@dataclasses.dataclass
class ReplicateSet:
    time: int
    data_points: dict[str, float]

    def join(self, rs):
        # assume that time is the same. TODO probably throw an error if it isn't
        return ReplicateSet(time=self.time, data_points=self.data_points | rs.data_points)

    def concentrations(self):
        return [x / (path_length * extinction) for x in self.data_points.values()]

    def mean_concentration(self):
        return statistics.mean(self.concentrations())

    def stdev_concentration(self):
        if len(self.concentrations()) < 2:
            return 0
        return statistics.stdev(self.concentrations())


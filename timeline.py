import dataclasses

from lmfit import Model

from absorbance import path_length, extinction


@dataclasses.dataclass
class Timeline:
    well: str
    # note: str  # TODO make this a function and test it
    # included: True  # TODO make this a function and test it
    fit_result: Model = dataclasses.field(default_factory=Model)
    fit: dict[str, float] = dataclasses.field(default_factory=dict)
    absorbances: list[float] = dataclasses.field(default_factory=list)
    r_squared: float = 0.0
    k_m: float = 0.0
    k_cat: float = 0.0

    def __init__(self, well):
        self.well = well
        self.absorbances = []
        self.fit = {}

    # TODO test
    def concentrations(self):
        return list(map(lambda y: y / (path_length * extinction), self.absorbances))

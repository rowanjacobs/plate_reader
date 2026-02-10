import dataclasses

from lmfit import Model

import outliers
from absorbance import path_length, extinction


@dataclasses.dataclass
class Timeline:
    well: str
    fit_result: Model = dataclasses.field(default_factory=Model)
    fit: dict[str, float] = dataclasses.field(default_factory=dict)
    absorbances: list[float] = dataclasses.field(default_factory=list)
    metabolite_k_ms: list[float] = dataclasses.field(default_factory=list)
    metabolite_k_cats: list[float] = dataclasses.field(default_factory=list)
    r_squared: float = 1.0
    k_m: float = 0.0
    k_cat: float = 0.0

    def __init__(self, well):
        self.well = well
        self.absorbances = []
        self.metabolite_k_ms = []
        self.metabolite_k_cats = []
        self.fit = {}

    def concentrations(self):
        return list(map(lambda y: y / (path_length * extinction), self.absorbances))

    def reject(self):
        return self.r_squared < 0.9 or outliers.grubbs_test(self.metabolite_k_ms, self.k_m) \
               or outliers.grubbs_test(self.metabolite_k_cats, self.k_cat)

    def k_m_output(self):
        if self.reject():
            return ''
        return self.k_m

    def k_cat_output(self):
        if self.reject():
            return ''
        return self.k_cat

    def k_cat_over_k_m(self):
        if self.reject() or self.k_m == 0.0:
            return ''
        return self.k_cat / self.k_m

    def r_squared_output(self):
        if self.reject():
            return ''
        return self.r_squared

    def why_reject(self):
        if not self.reject():
            return ''
        if self.r_squared < 0.9:
            return f'R²={self.r_squared}'
        if outliers.grubbs_test(self.metabolite_k_ms, self.k_m):
            return f'Kₘ={self.k_m}'
        if outliers.grubbs_test(self.metabolite_k_cats, self.k_cat):
            return f'kcat={self.k_cat}'
        return ''

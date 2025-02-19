import math
import unittest

from hypothesis import given, strategies as st
from lmfit import create_params

from kinetics_modeling import objective


class TestKineticsModeling(unittest.TestCase):
    @given(st.floats(min_value=1e-9, max_value=10),  # s0
           st.floats(min_value=1e-9, max_value=100),  # k_m
           st.floats(min_value=1e-9, max_value=100),  # v_max
           st.integers(min_value=0, max_value=6000))  # t
    def test_objective_matches_michaelis_menten_kinetics(self, s0, k_m, v_max, t):
        params = create_params(s0=s0, k_m=k_m, v_max=v_max)
        model_s = objective(params, t, 0)
        # $$Vt = ([S]_0-[S]) + K_m \ln\frac{[S]_0}{[S]}$$
        vt = (s0 - model_s) + k_m * math.log(s0 / model_s)
        if v_max*t == 0:
            self.assertAlmostEqual(vt, v_max*t, places=5)
        else:
            self.assertAlmostEqual(v_max*t/vt, 1, places=5)


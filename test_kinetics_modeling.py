import math
import unittest
from unittest import mock

from hypothesis import given, strategies as st
from lmfit import create_params

from kinetics_modeling import objective, fit, objective_leastsq, curve_params


class TestKineticsModeling(unittest.TestCase):
    @given(st.floats(min_value=1e-9, max_value=10),  # s0
           st.floats(min_value=1e-9, max_value=1e-3),  # k_m
           st.floats(min_value=1e-100, max_value=100),  # k_cat
           st.integers(min_value=0, max_value=6000))  # t
    def test_objective_matches_michaelis_menten_kinetics(self, s0, k_m, k_cat, t):
        params = create_params(e=0.05, k_m=k_m, k_cat=k_cat)
        v_max = k_cat * 0.05
        model_s = objective(params, t, 0, s0)
        # $$Vt = ([S]_0-[S]) + K_m \ln\frac{[S]_0}{[S]}$$
        self.assertNotEqual(model_s, 0)  # TODO is this math correct?
        vt = (s0 - model_s) + k_m * math.log(s0 / model_s)
        if v_max * t == 0:
            self.assertAlmostEqual(vt, v_max * t, places=5)
        else:
            self.assertAlmostEqual(v_max * t / vt, 1, places=5)

    @mock.patch('kinetics_modeling.create_params', autospec=True)
    def test_curve_params(self, mock_params):
        mock_params.return_value = 'pineapple'

        self.assertEqual(curve_params(), 'pineapple')

        mock_params.assert_called_once_with(e={'value': 0.05, 'vary': False},
                                            k_m={'value': 0.05, 'min': 1e-9, 'max': 1e-3},
                                            k_cat={'value': 1.5, 'min': 1e-100})

    @mock.patch('kinetics_modeling.Minimizer', autospec=True)
    @mock.patch('kinetics_modeling.curve_params', autospec=True)
    def test_fit(self, mock_params, mock_minimizer):
        mock_params.return_value = 12345678

        instance = mock_minimizer.return_value
        instance.minimize.return_value = 1234

        t = [0, 5, 10, 15]
        data = [1, 2, 3, 4]

        result = fit(t, data)
        self.assertEqual(1234, result)

        mock_params.assert_called_once()
        mock_minimizer.assert_called_once_with(objective_leastsq, 12345678, fcn_args=(t, data))
        instance.minimize.assert_called_once_with(method='leastsq')

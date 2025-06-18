import math
from typing import List

from lmfit import create_params, Minimizer, report_fit, Parameters
from numpy import log, exp

# define objective function: returns the array to be minimized
from scipy.special import lambertw

e0 = 1.14e-6  # see Benchling for [E]_0


def objective(params: Parameters, t: int, data: float, s0: float):
    e = params['e']
    k_m = params['k_m']
    k_cat = params['k_cat']
    v_max = k_cat * e
    # approximation of k_m * lambertw(s0 / k_m * exp(s0 / k_m - (v_max * t) / k_m)))
    model = k_m * approx_lambert_w(s0, k_m, v_max, t)
    return data - model


def approx_lambert_w(s0: float, k_m: float, v_max: float, t: int):
    log_term = log(s0 / k_m) + (s0 / k_m) - (v_max * t / k_m)
    if math.isnan(log_term):
        # TODO proper error handling
        raise ValueError(f'Got NaN value for objective function at s0 {s0}, k_m {k_m}, v_max {v_max}, t {t}')
    if log_term > 600:  # large log_term, use asymptotic formula
        return log_term - log(log_term) + log(log_term) / log_term
    if log_term <= -100:  # small log_term, use linear approximation
        return exp(log_term)
    return lambertw(exp(log_term)).real


def _s0(data: List[float]):
    return max(data) - min(data)


def objective_leastsq(params: Parameters, t: List[int], data: List[float]):
    return [objective(params, t[i], data[i] - min(data), _s0(data)) for i in range(len(data))]


def curve_params():
    return create_params(e={'value': e0, 'vary': False},
                         k_m={'value': 5e-5, 'min': 1e-12, 'max': 1e3},  # 50 µM
                         k_cat={'value': 1.5, 'min': 1e-100}
                         )


def fit(t: List[int], data: List[float]):
    params = curve_params()
    minimizer = Minimizer(objective_leastsq, params, fcn_args=(t, data))
    # Levenberg-Marquardt is the default method
    # but let's specify it explicitly anyway
    # it requires an objective function that provides an array
    result = minimizer.minimize(method='leastsq')
    return result

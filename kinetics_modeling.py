import math
from typing import List

from lmfit import create_params, Minimizer, report_fit, Parameters
from numpy import log, exp

# define objective function: returns the array to be minimized
from scipy.special import lambertw


def objective(params: Parameters, t: int, data: float, s0: float):
    k_m = params['k_m']
    v_max = params['v_max']
    # approximation of k_m * lambertw(s0 / k_m * exp(s0 / k_m - (v_max * t) / k_m))
    model = k_m * _approx_lambert_w(s0, k_m, v_max, t)
    return model - data


def _approx_lambert_w(s0: float, k_m: float, v_max: float, t: int):
    log_term = log(s0 / k_m) + (s0 / k_m) - (v_max * t / k_m)
    if math.isnan(log_term):
        # TODO proper error handling
        raise ValueError(f'Got NaN value for objective function at s0 {s0}, k_m {k_m}, v_max {v_max}, t {t}')
    if log_term > 10:  # large log_term, use asymptotic formula
        return log_term - log(log_term) + log(log_term) / log_term
    if log_term <= -5:  # small log_term, use linear approximation
        return exp(log_term)
    return lambertw(exp(log_term)).real


def _s0(data: List[float]):
    from absorbance import path_length, extinction
    return data[0] / (path_length * extinction)


def objective_leastsq(params: Parameters, t: List[int], data: List[float]):
    return [objective(params, t[i], data[i], _s0(data)) for i in range(len(data))]


def curve_params():
    return create_params(k_m={'value': 0.05, 'min': 1e-9, 'max': 1e-3},  # 50 µM
                         v_max={'value': 0.075, 'min': 1e-9}  # = 1.5*0.05 = kcat * [E]_0—see Benchling for [E]_0
                         )


def fit(t: List[int], data: List[float]):
    params = curve_params()
    minimizer = Minimizer(objective_leastsq, params, fcn_args=(t, data))
    # Levenberg-Marquardt is the default method
    # but let's specify it explicitly anyway
    # it requires an objective function that provides an array
    result = minimizer.minimize(method='leastsq')
    return result

import copy
import math
from typing import List

import numpy
from lmfit import create_params, Minimizer, Parameters
from lmfit.models import LinearModel
from numpy import log, exp

# define objective function: returns the array to be minimized
from scipy.special import lambertw

import constants
from constants import ENZYME_CONCENTRATION, STARTING_KCAT_ESTIMATION, STARTING_K_M_ESTIMATION, MIN_K_M


def objective(params: Parameters, t: int, data: float, s0: float):
    e = params['e']
    k_m = params['k_m']
    k_cat = params['k_cat']
    v_max = k_cat * e
    # approximation of k_m * lambertw(s0 / k_m * exp(s0 / k_m - (v_max * t) / k_m)))
    model = k_m * approx_lambert_w(s0, k_m, v_max, t)
    return data - model


def approx_lambert_w(s0: float, k_m: float, v_max: float, t: int):
    try:
        log_term = log(s0 / k_m) + (s0 / k_m) - (v_max * t / k_m)
    except RuntimeWarning:
        # TODO proper error handling
        raise ValueError(f'Got div by 0 for objective function at s0 {s0}, k_m {k_m}, v_max {v_max}, t {t}'
                         .format(s0=s0, k_m=k_m, v_max=v_max, t=t))
    if math.isnan(log_term):
        # TODO proper error handling
        raise ValueError(f'Got NaN value for objective function at s0 {s0}, k_m {k_m}, v_max {v_max}, t {t}'
                         .format(s0=s0, k_m=k_m, v_max=v_max, t=t))
    if log_term > 600:  # large log_term, use asymptotic formula
        return log_term - log(log_term) + log(log_term) / log_term
    if log_term <= -100:  # small log_term, use linear approximation
        return exp(log_term)
    return lambertw(exp(log_term)).real


def _s0(data: List[float]):
    return max(data)


def objective_leastsq(params: Parameters, t: List[int], data: List[float]):
    return [objective(params, t[i], data[i], _s0(data)) for i in range(len(data))]


def curve_params(s0=1e3):
    return create_params(e={'value': ENZYME_CONCENTRATION, 'vary': False},
                         k_m={'value': STARTING_K_M_ESTIMATION, 'min': MIN_K_M, 'max': s0},
                         k_cat={'value': STARTING_KCAT_ESTIMATION, 'min': 1e-100}
                         )


def fit(t: List[int], data: List[float]):
    s0 = _s0(data)
    if not (constants.CAP_KM_AT_S0 and s0 > 0.0):
        s0 = 1e3
    params = curve_params(s0=s0)
    minimizer = Minimizer(objective_leastsq, params, fcn_args=(t, data))
    # Levenberg-Marquardt is the default method
    # but let's specify it explicitly anyway
    # it requires an objective function that provides an array
    result = minimizer.minimize(method='leastsq')

    linear_result = linear_fit(t, data)
    linear_kcat = -1 * linear_result.params['slope'].value.item() / ENZYME_CONCENTRATION
    nonlinear_k_m = result.params['k_m'].value.item()
    try:
        nonlinear_kcat = result.params['k_cat'].value.item()
    except AttributeError:
        nonlinear_kcat = result.params['k_cat'].value

    if math.isclose(nonlinear_k_m, 1e-8, abs_tol=1e-9) and not math.isclose(linear_kcat, nonlinear_kcat):
        linear_result.params['k_cat'] = copy.deepcopy(linear_result.params['slope'])
        linear_result.params['k_cat'].value = linear_kcat
        linear_result.params['k_m'] = copy.deepcopy(linear_result.params['intercept'])
        linear_result.params['k_m'].value = numpy.float64(-1)
        return linear_result

    return result


# because this is used to index into an array, we return the index 1 *after* it goes flat
def find_steady_state(data):
    for i in range(1, len(data)-2):
        if data[i] <= 0.00001 or math.isclose(data[i], 0.0001):
            return i+1
    return len(data)


def linear_fit(t: List[int], data: List[float]):
    lmodel = LinearModel()
    params = lmodel.make_params(slope=-ENZYME_CONCENTRATION, intercept=600)

    # cut out the steady-state part of the data
    cutoff_index = find_steady_state(data)

    result = lmodel.fit(data[:cutoff_index], params=params, x=t[:cutoff_index])

    return result

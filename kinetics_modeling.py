from lmfit import create_params, Minimizer, report_fit
from numpy import log, exp

# define objective function: returns the array to be minimized
from scipy.special import lambertw


def objective(params, t, data):
    # TODO calculate s0 directly from initial absorbance value
    s0 = params['s0']
    k_m = params['k_m']
    v_max = params['v_max']
    # approximation of  k_m * lambertw(s0 / k_m * exp(s0 / k_m - (v_max * t) / k_m))
    model = k_m * _approx_lambert_w(s0, k_m, v_max, t)
    return model - data


def _approx_lambert_w(s0, k_m, v_max, t):
    log_term = log(s0 / k_m) + (s0 / k_m) - (v_max * t / k_m)
    if log_term > 10:  # large log_term, use asymptotic formula
        return log_term - log(log_term) + log(log_term) / log_term
    if log_term <= -5:  # small log_term, use linear approximation
        return exp(log_term)
    return lambertw(exp(log_term)).real


def objective_leastsq(params, t, data):
    return [objective(params, t, datum) for datum in data]


def curve_params():
    return create_params(s0=2,  # see Benchling protocol
                         k_m=0.05,  # 50 µM
                         v_max=1.5 * 0.05  # kcat * [E]_0—see Benchling for [E]_0
                         )


def fit(t, data):
    params = curve_params()
    minimizer = Minimizer(objective_leastsq, params, fcn_args=(t, data))
    # Levenberg-Marquardt is the default method
    # but let's specify it explicitly anyway
    # it requires an objective function that provides an array
    result = minimizer.minimize(method='leastsq')
    return result

import lmfit
from lmfit import create_params
from numpy import exp
from scipy.special import lambertw


# define objective function: returns the array to be minimized
def objective(params, t, data):
    s0 = params['[S]_0']
    k_m = params['K_m']
    v_max = params['V_max']
    # TODO: some assertions to catch weird params? to ensure W0 is real-valued?
    model = k_m * lambertw(s0 / k_m * exp(s0 / k_m - (v_max * t) / k_m))
    return model - data


def curve_params():
    return create_params(s0=2,  # see Benchling protocol
                         k_m=0.05,  # 50 µM
                         v_max=1.5 * 0.05  # kcat * [E]_0—see Benchling for [E]_0
                         )

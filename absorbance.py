# ε₃₄₀(NADH) = 6220 M⁻¹cm⁻¹
# A = εlc

path_length = 0.195565054
extinction = 6220


def concentration_from_absorbance(absorbance):
    return absorbance / (path_length * extinction)


def concentration_of_array(absorbance_data):
    return [[concentration_from_absorbance(x) for x in line] for line in absorbance_data]

import math

mock_pr_output = """


Software Version	3.15.15



Experiment File Path:	C:\\Users\\Public\\Documents\\Experiments\\241112 wt gs concentration screen for team screening 2.xpt
Protocol File Path:	C:\\Users\\Public\\Documents\\Protocols\\384well_nadh_screening.prt



Plate Number	Plate 1
Date	11/12/2024
Time	1:50:24 PM
Reader Type:	Synergy Neo2
Reader Serial Number:	23082103
Reading Type	Reader

Procedure Details

Plate Type	Corning 384 flat bottom (Use plate lid)
Eject plate on completion	
Set Temperature	Setpoint 25∞C, Gradient 0 ∞C
	Preheat before moving to next step
Start Kinetic	Runtime 1:00:00 (HH:MM:SS), Interval 0:00:12, 301 Reads
    Read	Absorbance Endpoint
	C1..C24
	Wavelengths:  340
	Read Speed: Normal,  Delay: 50 msec,  Measurements/Data Point: 8
End Kinetic	

340

Time	T∞ 340	A1	A2	A3	A4
0:00:00	25.0	1.691	1.736	1.787	1.837
0:00:12	25.0    2.069	2.065	1.907	1.480

Results
	1	2	3	4
C	29.500	-5.650	-54.400	-42.350	Max V [340]
	0.835	0.940	0.966	1.000	R-Squared [340]
	0:00:24	0:53:12	0:00:24	0:01:24	t at Max V [340]
	?????	0:30:17	?????	0:00:44	Lagtime [340]
"""

mock_data_lines = """Time	T∞ 340	A1	A2	A3	A4
0:00:00	25.0	1.691	1.736	1.787	1.837
0:00:12	25.0    2.069	2.065	1.907	1.480
"""

# the last element in the last array is an outlier
mock_data = [
    [1.691, 1.736, 1.787, 1.837],
    [2.069, 2.065, 1.907, 1.480]
]

mock_data_concentration = [
    [1.691 / (0.195565054 * 6220), 1.736 / (0.195565054 * 6220), 1.787 / (0.195565054 * 6220),
     1.837 / (0.195565054 * 6220)],
    [2.069 / (0.195565054 * 6220), 2.065 / (0.195565054 * 6220), 1.907 / (0.195565054 * 6220),
     1.480 / (0.195565054 * 6220)]
]

mock_concentration_means = [0.0015539520359622461, 0.0015156564318489058]

mock_concentration_stdevs = [0.0001684663931449787, 4.9553117790144295e-05]

mock_concentration_grubbs_max = [0.8723, 0.8188]

mock_statistics_lines = """	1	2	3	4
C	29.500	-5.650	-54.400	-42.350	Max V [340]
	0.835	0.940	0.966	1.000	R-Squared [340]
	0:00:24	0:53:12	0:00:24	0:01:24	t at Max V [340]
	?????	0:30:17	?????	0:00:44	Lagtime [340]
"""

mock_statistics = {
    'Max V': [29.500, -5.650, -54.400, -42.350],
    'R-Squared': [0.835, 0.940, 0.966, 1.000],
    't at Max V': [24, 53 * 60 + 12, 24, 60 + 24],
    'Lagtime': [30 * 60 + 17, 44]
}


def assert_almost_equal(test_case, array1, array2, rel_tol=1e-9, abs_tol=0.0, level=0):
    """
    Generalized matcher to assert that two arrays are approximately equal (supports nested arrays).

    Args:
        test_case: The unittest.TestCase instance.
        array1: First array (list or tuple) to compare.
        array2: Second array (list or tuple) to compare.
        rel_tol: Relative tolerance for floating-point comparison.
        abs_tol: Absolute tolerance for floating-point comparison.
        level: Recursion level, used to differentiate array depth during comparison.

    Raises:
        AssertionError: If the arrays are not approximately equal.
    """
    # Ensure the arrays have the same length
    if len(array1) != len(array2):
        test_case.fail(f"Arrays at level {level} have different lengths: {len(array1)} != {len(array2)}")

    # Compare element-wise, recursively for nested arrays
    for i, (x, y) in enumerate(zip(array1, array2)):
        if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
            # Recursively compare subarrays
            assert_almost_equal(test_case, x, y, rel_tol, abs_tol, level + 1)
        else:
            # Compare floats using math.isclose for each element
            if not math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol):
                test_case.fail(
                    f"Arrays differ at level {level}, index {i}: {x} != {y} within tolerance "
                    f"(rel_tol={rel_tol}, abs_tol={abs_tol})"
                )


# Specific matchers that use the generalized matcher

def assert_arrays_almost_equal(test_case, array1, array2, rel_tol=1e-9, abs_tol=0.0):
    """
    Assert that two flat arrays (1D lists) are approximately equal.
    """
    assert_almost_equal(test_case, array1, array2, rel_tol, abs_tol)


def assert_arrays_of_arrays_almost_equal(test_case, array1, array2, rel_tol=1e-9, abs_tol=0.0):
    """
    Assert that two arrays of arrays (2D lists) are approximately equal.
    """
    assert_almost_equal(test_case, array1, array2, rel_tol, abs_tol)


def assert_dicts_with_float_arrays_almost_equal(test_case, dict1, dict2, rel_tol=1e-9, abs_tol=0.0):
    """
    Custom matcher to assert that two dictionaries with string keys and float array values are approximately equal.

    Args:
        test_case: The unittest.TestCase instance.
        dict1: The first dictionary to compare (with string keys and list/array of floats as values).
        dict2: The second dictionary to compare (with string keys and list/array of floats as values).
        rel_tol: Relative tolerance for floating-point comparison.
        abs_tol: Absolute tolerance for floating-point comparison.

    Raises:
        AssertionError: If the dictionaries are not approximately equal.
    """
    # Ensure the dictionaries have the same keys
    if dict1.keys() != dict2.keys():
        test_case.fail(f"Dictionaries have different keys: {dict1.keys()} != {dict2.keys()}")

    # Compare the values for each key using the reused array comparison
    for key in dict1:
        array1 = dict1[key]
        array2 = dict2[key]

        # Use the assert_arrays_almost_equal function to compare the arrays
        assert_arrays_almost_equal(test_case, array1, array2, rel_tol=rel_tol, abs_tol=abs_tol)

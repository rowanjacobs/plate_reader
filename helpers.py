import math
import unittest

from replicate_set import ReplicateSet
from replicate_set_timeline import ReplicateSetTimeline

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

Time	T∞ 340	A1	A2	A3	A4	B1	B2	B3	B4
0:00:00	25.0	1.691	1.736	1.787	1.837	2.069	2.065	1.907	1.480
0:00:12	25.0    1.791	1.836	1.887	1.937	2.169	2.165	2.007	1.580

Results
	1	2	3	4
C	29.500	-5.650	-54.400	-42.350	Max V [340]
	0.835	0.940	0.966	1.000	R-Squared [340]
	0:00:24	0:53:12	0:00:24	0:01:24	t at Max V [340]
	?????	0:30:17	?????	0:00:44	Lagtime [340]
"""

mock_long_data_lines = """Time	T° 340	A1	A2	A3	A4	A5	A6	A7	A8	A9	A10	A11	A12	A13	A14	A15	A16	A17	A18	A19	A20	A21	A22	A23	A24	B1	B2	B3	B4	B5	B6	B7	B8	B9	B10	B11	B12	B13	B14	B15	B16	B17	B18	B19	B20	B21	B22	B23	B24	C1	C2	C3	C4	C5	C6	C7	C8	C9	C10	C11	C12	C13	C14	C15	C16	C17	C18	C19	C20	C21	C22	C23	C24	D1	D2	D3	D4	D5	D6	D7	D8	D9	D10	D11	D12	D13	D14	D15	D16	D17	D18	D19	D20	D21	D22	D23	D24	E1	E2	E3	E4	E5	E6	E7	E8	E9	E10	E11	E12	E13	E14	E15	E16	E17	E18	E19	E20	E21	E22	E23	E24	F1	F2	F3	F4	F5	F6	F7	F8	F9	F10	F11	F12	F13	F14	F15	F16	F17	F18	F19	F20	F21	F22	F23	F24	G1	G2	G3	G4	G5	G6	G7	G8	G9	G10	G11	G12	G13	G14	G15	G16	G17	G18	G19	G20	G21	G22	G23	G24	H1	H2	H3	H4	H5	H6	H7	H8	H9	H10	H11	H12	H13	H14	H15	H16	H17	H18	H19	H20	H21	H22	H23	H24	I1	I2	I3	I4	I5	I6	I7	I8	I9	I10	I11	I12	I13	I14	I15	I16	I17	I18	I19	I20	I21	I22	I23	I24	J1	J2	J3	J4	J5	J6	J7	J8	J9	J10	J11	J12	J13	J14	J15	J16	J17	J18	J19	J20	J21	J22	J23	J24	K1	K2	K3	K4	K5	K6	K7	K8	K9	K10	K11	K12	K13	K14	K15	K16	K17	K18	K19	K20	K21	K22	K23	K24	L1	L2	L3	L4	L5	L6	L7	L8	L9	L10	L11	L12	L13	L14	L15	L16	L17	L18	L19	L20	L21	L22	L23	L24	M1	M2	M3	M4	M5	M6	M7	M8	M9	M10	M11	M12	M13	M14	M15	M16	M17	M18	M19	M20	M21	M22	M23	M24	N1	N2	N3	N4	N5	N6	N7	N8	N9	N10	N11	N12	N13	N14	N15	N16	N17	N18	N19	N20	N21	N22	N23	N24	O1	O2	O3	O4	O5	O6	O7	O8	O9	O10	O11	O12	O13	O14	O15	O16	O17	O18	O19	O20	O21	O22	O23	O24	P1	P2	P3	P4	P5	P6	P7	P8	P9	P10	P11	P12	P13	P14	P15	P16	P17	P18	P19	P20	P21	P22	P23	P24
0:00:00	25.0																																																																																																	0.337	0.486	0.332	0.394	0.340	0.419	0.347	0.459	0.327	0.410	0.323	0.406	0.327	0.382	0.335	0.442	0.324	0.387	0.321	0.389	0.316	0.353	0.319	0.316																																																																																																																																																																																																																																																																								
0:00:12	25.0																																																																																																	0.334	0.481	0.333	0.389	0.340	0.416	0.347	0.500	0.327	0.402	0.323	0.400	0.326	0.375	0.335	0.438	0.322	0.383	0.320	0.384	0.314	0.348	0.317	0.314																																																																																																																																																																																																																																																																								
0:00:24	25.0																																																																																																	0.334	0.475	0.333	0.382	0.340	0.409	0.347	0.521	0.327	0.394	0.322	0.394	0.326	0.369	0.333	0.431	0.320	0.376	0.319	0.378	0.313	0.344	0.315	0.310																																																																																																																																																																																																																																																																								
0:00:36	25.0																																																																																																	0.334	0.467	0.333	0.374	0.340	0.401	0.346	0.535	0.325	0.386	0.322	0.387	0.326	0.362	0.332	0.423	0.319	0.370	0.318	0.372	0.311	0.339	0.314	OVRFLW																																																																																																																																																																																																																																																																								
"""

mock_long_data_single_lines = """Time	T° 340	A1	A2	A3	A4	A5	A6	A7	A8	A9	A10	A11	A12	A13	A14	A15	A16	A17	A18	A19	A20	A21	A22	A23	A24	B1	B2	B3	B4	B5	B6	B7	B8	B9	B10	B11	B12	B13	B14	B15	B16	B17	B18	B19	B20	B21	B22	B23	B24	C1	C2	C3	C4	C5	C6	C7	C8	C9	C10	C11	C12	C13	C14	C15	C16	C17	C18	C19	C20	C21	C22	C23	C24	D1	D2	D3	D4	D5	D6	D7	D8	D9	D10	D11	D12	D13	D14	D15	D16	D17	D18	D19	D20	D21	D22	D23	D24	E1	E2	E3	E4	E5	E6	E7	E8	E9	E10	E11	E12	E13	E14	E15	E16	E17	E18	E19	E20	E21	E22	E23	E24	F1	F2	F3	F4	F5	F6	F7	F8	F9	F10	F11	F12	F13	F14	F15	F16	F17	F18	F19	F20	F21	F22	F23	F24	G1	G2	G3	G4	G5	G6	G7	G8	G9	G10	G11	G12	G13	G14	G15	G16	G17	G18	G19	G20	G21	G22	G23	G24	H1	H2	H3	H4	H5	H6	H7	H8	H9	H10	H11	H12	H13	H14	H15	H16	H17	H18	H19	H20	H21	H22	H23	H24	I1	I2	I3	I4	I5	I6	I7	I8	I9	I10	I11	I12	I13	I14	I15	I16	I17	I18	I19	I20	I21	I22	I23	I24	J1	J2	J3	J4	J5	J6	J7	J8	J9	J10	J11	J12	J13	J14	J15	J16	J17	J18	J19	J20	J21	J22	J23	J24	K1	K2	K3	K4	K5	K6	K7	K8	K9	K10	K11	K12	K13	K14	K15	K16	K17	K18	K19	K20	K21	K22	K23	K24	L1	L2	L3	L4	L5	L6	L7	L8	L9	L10	L11	L12	L13	L14	L15	L16	L17	L18	L19	L20	L21	L22	L23	L24	M1	M2	M3	M4	M5	M6	M7	M8	M9	M10	M11	M12	M13	M14	M15	M16	M17	M18	M19	M20	M21	M22	M23	M24	N1	N2	N3	N4	N5	N6	N7	N8	N9	N10	N11	N12	N13	N14	N15	N16	N17	N18	N19	N20	N21	N22	N23	N24	O1	O2	O3	O4	O5	O6	O7	O8	O9	O10	O11	O12	O13	O14	O15	O16	O17	O18	O19	O20	O21	O22	O23	O24	P1	P2	P3	P4	P5	P6	P7	P8	P9	P10	P11	P12	P13	P14	P15	P16	P17	P18	P19	P20	P21	P22	P23	P24
0:00:00	25.0	1.218	1.062	1.149	1.180	1.251	1.266	1.200	1.262	1.192	1.304	1.246	1.315	1.211	1.265	1.257	1.251																																																																																																																																																																																																																																																																																																																																																																																
0:00:12	25.0	1.200	1.048	1.132	1.165	1.230	1.248	1.178	1.244	1.170	1.285	1.219	1.298	1.191	1.247	1.240	1.234																																																																																																																																																																																																																																																																																																																																																																																
0:00:24	25.0	1.174	1.029	1.112	1.146	1.204	1.226	1.152	1.220	1.143	1.258	1.190	1.273	1.166	1.224	1.218	1.211
"""

mock_data_lines = """Time	T∞ 340	A1	A2	A3	A4	B1	B2	B3	B4
0:00:00	25.0	1.691	1.736	1.787	1.837	2.069	2.065	1.907	1.480
0:00:12	25.0    1.791	1.836	1.887	1.937	2.169	2.165	2.007	1.580
"""

mock_overflow_lines = """Time	T∞ 340	A1	A2	A3	A4	B1	B2	B3	B4
0:00:00	25.0	1.691	1.736	1.787	1.837	2.069	2.065	1.907	1.480
0:00:12	25.0    1.791	1.836	1.887	1.937	2.169	2.165	2.007	OVRFLW
"""

# the last element in the first array is an outlier
mock_data = [
    [1.691, 1.736, 1.787, 1.837, 2.069, 2.065, 1.907, 1.480],
    [1.791, 1.836, 1.887, 1.937, 2.169, 2.165, 2.007, 1.580],
]

mock_data_overflow = [
    [1.691, 1.736, 1.787, 1.837, 2.069, 2.065, 1.907, 1.480],
    [1.791, 1.836, 1.887, 1.937, 2.169, 2.165, 2.007, 5.000],
]

mock_data_replicate_sets = [
    ReplicateSetTimeline('A1A2B1B2', [
        ReplicateSet(time=0, well='A1A2B1B2', data_points=[1.691, 1.736, 2.069, 2.065]),
        ReplicateSet(time=12, well='A1A2B1B2', data_points=[1.791, 1.836, 2.169, 2.165])
    ]),
    ReplicateSetTimeline('A3A4B3B4', [
        ReplicateSet(time=0, well='A3A4B3B4', data_points=[1.787, 1.837, 1.907, 1.480]),
        ReplicateSet(time=12, well='A3A4B3B4', data_points=[1.887, 1.937, 2.007, 1.580])
    ])
]

mock_data_concentration = [
    [1.691 / (0.195565054 * 6220), 1.736 / (0.195565054 * 6220), 1.787 / (0.195565054 * 6220),
     1.837 / (0.195565054 * 6220), 2.069 / (0.195565054 * 6220), 2.065 / (0.195565054 * 6220),
     1.907 / (0.195565054 * 6220), 1.480 / (0.195565054 * 6220)],
    [1.791 / (0.195565054 * 6220), 1.836 / (0.195565054 * 6220), 1.887 / (0.195565054 * 6220),
     1.937 / (0.195565054 * 6220), 2.169 / (0.195565054 * 6220), 2.165 / (0.195565054 * 6220),
     2.007 / (0.195565054 * 6220), 1.580 / (0.195565054 * 6220)]
]

mock_concentration_means = [0.0014497523689561808, 0.0015512802496287573, 0.0017403605132295065, 0.0014333106069039417]

mock_concentration_stdevs = [5.204754846191094e-05, 4.110440513059772e-05, 4.750123418093657e-05, 0.000208151776831809]

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


def assert_almost_equal(test_case, x, y, rel_tol=1e-9, abs_tol=0.0):
    if not math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol):
        test_case.fail(
            f"{x} != {y} within tolerance (rel_tol={rel_tol}, abs_tol={abs_tol})"
        )


def assert_arrays_almost_equal(test_case, array1, array2, rel_tol=1e-9, abs_tol=0.0, level=0):
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
            assert_arrays_almost_equal(test_case, x, y, rel_tol, abs_tol, level + 1)
        else:
            # Compare floats using math.isclose for each element
            if not math.isclose(x, y, rel_tol=rel_tol, abs_tol=abs_tol):
                test_case.fail(
                    f"Arrays differ at level {level}, index {i}: {x} != {y} within tolerance "
                    f"(rel_tol={rel_tol}, abs_tol={abs_tol})"
                )


# Specific matchers that use the generalized matcher


def assert_arrays_of_arrays_almost_equal(test_case, array1, array2, rel_tol=1e-9, abs_tol=0.0):
    """
    Assert that two arrays of arrays (2D lists) are approximately equal.
    """
    assert_arrays_almost_equal(test_case, array1, array2, rel_tol, abs_tol)


def assert_replicate_sets_almost_equal(test_case, rs1: ReplicateSet, rs2: ReplicateSet, rel_tol=1e-9, abs_tol=0.0):
    """
    Assert that two ReplicateSets are approximately equal.
    """
    test_case.assertEqual(rs1.time, rs2.time)
    test_case.assertEqual(rs1.well, rs2.well)
    assert_arrays_almost_equal(test_case, rs1.data_points, rs2.data_points)


def assert_replicate_set_timelines_almost_equal(test_case: unittest.TestCase, rstl1: ReplicateSetTimeline,
                                                rstl2: ReplicateSetTimeline, rel_tol=1e-9, abs_tol=0.0):
    """
    Assert that two ReplicateSetTimelines are approximately equal.
    """
    test_case.assertEqual(rstl1.well, rstl2.well)
    for i, rs in enumerate(rstl1.replicate_sets):
        assert_replicate_sets_almost_equal(test_case, rs, rstl2.replicate_sets[i])


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

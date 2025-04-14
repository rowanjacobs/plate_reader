import math
import unittest

from replicate_set import ReplicateSet
from replicate_set_timeline import ReplicateSetTimeline


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
import os
import sys
import pytest
import math
import numpy as np

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from python_source.cordic_trig_generator import CORDICTrigGenerator


def test_fixed_point_format():
    cordic_trig_generator = CORDICTrigGenerator(16, "2.30")
    assert cordic_trig_generator.num_total_bits == 32
    assert cordic_trig_generator.num_whole_bits == 2
    assert cordic_trig_generator.num_fractional_bits == 30
    assert cordic_trig_generator.scaling_factor == 2**30

    with pytest.raises(ValueError):
        CORDICTrigGenerator(16, "2.30.1")

    with pytest.raises(ValueError):
        CORDICTrigGenerator(16, "65.0")

    with pytest.raises(ValueError):
        CORDICTrigGenerator(16, "-2.30")

    with pytest.raises(ValueError):
        CORDICTrigGenerator(16, "2.-30")


def test_ensure_iterations_are_greater_than_zero():
    with pytest.raises(ValueError):
        CORDICTrigGenerator(0, "2.30")

    with pytest.raises(ValueError):
        CORDICTrigGenerator(-1, "2.30")


def test_atan_table():
    cordic_trig_generator = CORDICTrigGenerator(16, "2.30")

    SCALING_FACTOR = 2**30

    for i in range(16):
        assert (
            cordic_trig_generator.ATAN_TABLE[i] == math.atan(2**-i) * SCALING_FACTOR
        )


def test_cos_k1():
    cordic_trig_generator = CORDICTrigGenerator(16, "2.30")
    cos_k1 = 1
    for i in range(16):
        cos_k1 *= np.cos(math.atan(2**-i))
    assert cos_k1 == cordic_trig_generator.cos_k1
    assert int(cos_k1 * 2**30) == cordic_trig_generator.cos_k1_scaled


def test_int_type():
    cordic_trig_generator = CORDICTrigGenerator(16, "2.30")
    assert cordic_trig_generator.fixed_point_typedef == "int32_t"

    cordic_trig_generator = CORDICTrigGenerator(16, "2.14")
    assert cordic_trig_generator.fixed_point_typedef == "int16_t"

    cordic_trig_generator = CORDICTrigGenerator(16, "2.56")
    assert cordic_trig_generator.fixed_point_typedef == "int64_t"

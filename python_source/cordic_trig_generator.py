import argparse
import math
import numpy as np


class CORDICTrigGenerator:
    def __init__(self, n, fixed_point_format):
        if n <= 0:
            raise ValueError("Number of iterations must be greater than zero")

        self.n = n
        self.parse_fixed_point_format(fixed_point_format)

        self.scaling_factor = 2**self.num_fractional_bits
        self.scaling_factor_str = f"(1 << {self.num_fractional_bits})"

        self.ATAN_TABLE_RAW = self.generate_atan_table()
        self.ATAN_TABLE = [
            int(val * self.scaling_factor) for val in self.ATAN_TABLE_RAW
        ]

        self.cos_k1 = self.generate_cos_k1()
        self.cos_k1_scaled = int(self.cos_k1 * self.scaling_factor)

        if self.num_total_bits <= 8:
            num_bits_to_use_for_typedef = 8
        elif self.num_total_bits <= 16:
            num_bits_to_use_for_typedef = 16
        elif self.num_total_bits <= 32:
            num_bits_to_use_for_typedef = 32
        else:
            num_bits_to_use_for_typedef = 64

        self._fixed_point_typedef = f"int{num_bits_to_use_for_typedef}_t"

    def generate_cos_k1(self):
        cos_k1 = 1
        for i in range(self.n):
            cos_k1 *= np.cos(math.atan(2**-i))
        return cos_k1

    def generate_atan_table(self):
        atan_table = np.zeros(self.n)
        for i in range(self.n):
            atan_table[i] = math.atan(2**-i)
        return atan_table

    def parse_fixed_point_format(self, fixed_point_format):
        # Split the fixed point format into the integer and fractional parts
        try:
            integer_part, fractional_part = fixed_point_format.split(".")
            self.num_whole_bits = int(integer_part)
            self.num_fractional_bits = int(fractional_part)
            self.num_total_bits = self.num_whole_bits + self.num_fractional_bits
        except ValueError:
            raise ValueError(
                "Invalid fixed point format: {}".format(fixed_point_format)
            )

        if self.num_total_bits > 64:
            raise ValueError("Total number of bits cannot exceed 64")

        if self.num_whole_bits < 0 or self.num_fractional_bits < 0:
            raise ValueError("Number of whole and fractional bits must be non-negative")

    def write_to_file(
        self,
        inc_dir,
        src_dir,
        file_name="cordic_trig",
        function_prepend="cordic_trig",
    ):
        inc_file_contents = f"""
#ifndef {file_name.upper()}_H
#define {file_name.upper()}_H

#include <stdint.h>

typedef {self._fixed_point_typedef} {function_prepend}_fixed_point_t;

/**
* @brief Get the sine and cosine values of the given angle in radians
*
* @param theta_rad Angle in radians
* @param sin_val Pointer to the sine value
* @param cos_val Pointer to the cosine value
*/
void {function_prepend}_get_sin_cos(float theta_rad, float *sin_val, float *cos_val);

#endif // {file_name.upper()}_H
"""
        inc_file_name = f"{inc_dir}/{file_name}.h"
        with open(inc_file_name, "w") as inc_file:
            inc_file.write(inc_file_contents)

        atan_table_as_string = "L, ".join([f"{val}" for val in self.ATAN_TABLE])
        # wrap the atan table as string in {}
        atan_table_as_string = "{" + atan_table_as_string + "L}"

        src_file_contents = f"""
#include "{file_name}.h"
#include <stddef.h>

#define ATAN_TABLE_SIZE {self.n}
#define FIXED_POINT_SCALING_FACTOR {self.scaling_factor} // {self.scaling_factor_str}
#define ONE_OVER_FIXED_POINT_SCALING_FACTOR (1.0F / (float)FIXED_POINT_SCALING_FACTOR)
#define COS_K1 {self.cos_k1_scaled} // {self.cos_k1} scaled by FIXED_POINT_SCALING_FACTOR

static const {function_prepend}_fixed_point_t ATAN_TABLE[ATAN_TABLE_SIZE] = {atan_table_as_string};

void {function_prepend}_get_sin_cos(float theta_rad, float *sin_val, float *cos_val) {{
    {function_prepend}_fixed_point_t x = COS_K1;
    {function_prepend}_fixed_point_t y = 0;
    {function_prepend}_fixed_point_t z = ({function_prepend}_fixed_point_t)(theta_rad * (float)FIXED_POINT_SCALING_FACTOR);

    // TODO: Condition the theta_rad to be within the range of -pi/2 to pi/2

    for (size_t i = 0; i < ATAN_TABLE_SIZE; i++) {{
        {function_prepend}_fixed_point_t x_new = x;
        {function_prepend}_fixed_point_t y_new = y;
        
        if (z >= 0) {{
            x_new = x - (y >> i);
            y_new = y + (x >> i);
            z -= ATAN_TABLE[i];
        }} else {{
            x_new = x + (y >> i);
            y_new = y - (x >> i);
            z += ATAN_TABLE[i];
        }}

        x = x_new;
        y = y_new;
    }}

    if (sin_val) {{
        *sin_val = (float)y * ONE_OVER_FIXED_POINT_SCALING_FACTOR;
    }}

    if (cos_val) {{
        *cos_val = (float)x * ONE_OVER_FIXED_POINT_SCALING_FACTOR;
    }}
}}
"""
        src_file_name = f"{src_dir}/{file_name}.c"

        with open(src_file_name, "w") as src_file:
            src_file.write(src_file_contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CORDIC Trigonometric Generator")
    parser.add_argument("--n", type=int, default=16, help="Number of iterations")
    parser.add_argument(
        "--fixed-point-format",
        type=str,
        default="2.30",
        help="Fixed point format, e.g., 2.30 where 2 is the integer part and 30 is the fractional part",
    )
    parser.add_argument(
        "--inc-dir",
        type=str,
        default="inc",
        help="Output header file directory",
    )
    parser.add_argument(
        "--src-dir",
        type=str,
        default="src",
        help="Output source directory",
    )

    parser.add_argument(
        "--file-name",
        type=str,
        default="cordic_trig_generated",
        help="Output file name",
    )

    parser.add_argument(
        "--function-prepend",
        type=str,
        default="cordic_trig",
        help="Prepend to function names",
    )

    args = parser.parse_args()

    cordic_trig_generator = CORDICTrigGenerator(args.n, args.fixed_point_format)

    cordic_trig_generator.write_to_file(
        args.inc_dir, args.src_dir, args.file_name, args.function_prepend
    )

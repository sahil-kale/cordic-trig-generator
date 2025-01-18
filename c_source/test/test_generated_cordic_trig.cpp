#include "CppUTest/TestHarness.h"
#include "math.h"

extern "C" {
#include "cordic_trig_generated.h"
}

TEST_GROUP(cordic_trig){void setup(){} void teardown(){}};

#define DEG_TO_RAD(deg) ((deg) * M_PI / 180.0)
#define ALLOWABLE_ERROR 0.001

TEST(cordic_trig, test_0_to_2pi) {
    for (float i = 0; i <= 360; i += 0.1) {
        float sin_val, cos_val;
        cordic_trig_get_sin_cos(DEG_TO_RAD(i), &sin_val, &cos_val);
        DOUBLES_EQUAL(sin(DEG_TO_RAD(i)), sin_val, ALLOWABLE_ERROR);
        DOUBLES_EQUAL(cos(DEG_TO_RAD(i)), cos_val, ALLOWABLE_ERROR);
    }
}
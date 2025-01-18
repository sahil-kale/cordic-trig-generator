#include "CppUTest/TestHarness.h"
#include "math.h"

extern "C" {
#include "cordic_trig_generated.h"
}

TEST_GROUP(cordic_trig){void setup(){} void teardown(){}};

TEST(cordic_trig, test_45_degrees) {
    float angle = 45.0;
    float sine = sin(angle * M_PI / 180);
    float cosine = cos(angle * M_PI / 180);
    float sine_cordic, cosine_cordic;
    cordic_trig_get_sin_cos(angle, &sine_cordic, &cosine_cordic);
    DOUBLES_EQUAL(sine, sine_cordic, 0.001);
    DOUBLES_EQUAL(cosine, cosine_cordic, 0.001);
}
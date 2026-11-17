import unittest

from speed_controller import SpeedController


class TestSpeedControllerBlackBox(unittest.TestCase):
    """
    Black-box tests for SpeedController.update_speed().

    Expected values are derived from the written requirements in
    README.md (Appendix A), not from the implementation. A speed limit
    of 60 km/h is used throughout so each test varies one input at a
    time against a known-valid baseline (clear / traffic 20 / slope 0 /
    safety off => 60.00).
    """

    def setUp(self):
        self.controller = SpeedController(speed_limit=60)

    # --- Road condition category partition ---

    def test_clear_road_nominal(self):
        # clear keeps the base speed unchanged: 60 * 1.0 = 60.
        self.assertEqual(self.controller.update_speed('clear', 20, 0), 60.00)

    def test_wet_road_multiplier(self):
        # wet applies a 0.85 multiplier: 60 * 0.85 = 51.
        self.assertEqual(self.controller.update_speed('wet', 20, 0), 51.00)

    def test_icy_road_multiplier(self):
        # icy applies a 0.6 multiplier: 60 * 0.6 = 36.
        self.assertEqual(self.controller.update_speed('icy', 20, 0), 36.00)

    # --- Safety mode category partition ---

    def test_safety_mode_enabled_caps_speed(self):
        # Safety mode caps the target at speed_limit - 10 = 50.
        self.controller.set_safety_mode(True)
        self.assertEqual(self.controller.update_speed('clear', 20, 0), 50.00)

    # --- Traffic density boundary values (nominal) ---

    def test_traffic_at_lower_reduction_boundary(self):
        # traffic_density == 50 is the first value that triggers -10.
        self.assertEqual(self.controller.update_speed('clear', 50, 0), 50.00)

    def test_traffic_at_upper_minus_ten_boundary(self):
        # traffic_density == 80 is still in the 50-80 band => -10.
        self.assertEqual(self.controller.update_speed('clear', 80, 0), 50.00)

    def test_traffic_above_eighty_boundary(self):
        # traffic_density == 81 is the first value above 80 => -20.
        self.assertEqual(self.controller.update_speed('clear', 81, 0), 40.00)

    # --- Slope angle behaviour ---

    def test_downhill_increases_speed(self):
        # Downhill (negative slope) adds the absolute value: 60 + 5 = 65.
        self.assertEqual(self.controller.update_speed('clear', 10, -5), 65.00)

    def test_uphill_decreases_speed(self):
        # Uphill (positive slope) subtracts the slope: 60 - 7 = 53.
        self.assertEqual(self.controller.update_speed('clear', 10, 7), 53.00)

    # --- Combined scenario (README Appendix A example) ---

    def test_combined_example_scenario(self):
        # icy (x0.6) -> 36, traffic 90 (>80) -> 16, downhill 5 -> 21,
        # safety mode clamps to <= 50, final 21.00.
        self.controller.set_safety_mode(True)
        self.assertEqual(self.controller.update_speed('icy', 90, -5), 21.00)


if __name__ == '__main__':
    unittest.main()

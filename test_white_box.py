import unittest

from speed_controller import SpeedController


class TestSpeedControllerWhiteBox(unittest.TestCase):
    """
    White-box tests for SpeedController, designed by studying the control
    flow of update_speed() so that every statement is executed at least
    once (100% statement coverage).
    """

    def setUp(self):
        self.controller = SpeedController(speed_limit=60)

    def test_invalid_traffic_density_raises(self):
        # Exercises the traffic_density range-validation raise.
        with self.assertRaises(ValueError):
            self.controller.update_speed('clear', 150, 0)

    def test_invalid_slope_angle_raises(self):
        # Exercises the slope_angle range-validation raise.
        with self.assertRaises(ValueError):
            self.controller.update_speed('clear', 20, 20)

    def test_invalid_road_condition_raises(self):
        # Exercises the road-condition else raise (valid numeric inputs).
        with self.assertRaises(ValueError):
            self.controller.update_speed('foggy', 20, 0)

    def test_wet_high_traffic_uphill_safety_off(self):
        # Covers: wet branch, traffic > 80 (-20), slope > 0 (uphill),
        # safety-off max() clamp.
        # 60 * 0.85 = 51 -> traffic 90 (-20) = 31 -> uphill 10 = 21.
        self.assertEqual(self.controller.update_speed('wet', 90, 10), 21.00)

    def test_icy_mid_traffic_downhill_safety_on(self):
        # Covers: set_safety_mode, icy branch, traffic in 50-80 (-10),
        # slope < 0 (downhill), safety-on min() clamp.
        # 60 * 0.6 = 36 -> traffic 70 (-10) = 26 -> downhill 5 = 31,
        # safety caps to 50 -> 31.00.
        self.controller.set_safety_mode(True)
        self.assertEqual(self.controller.update_speed('icy', 70, -5), 31.00)

    def test_clear_low_traffic_flat_safety_off(self):
        # Covers: clear branch, traffic < 50 (no adjustment), slope == 0
        # (neither uphill nor downhill), safety-off max() clamp.
        self.assertEqual(self.controller.update_speed('clear', 20, 0), 60.00)


if __name__ == '__main__':
    unittest.main()

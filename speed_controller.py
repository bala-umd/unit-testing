class SpeedController:
    """
    Controls the speed of an autonomous vehicle based on a set
    of input parameters.
    """

    def __init__(self, speed_limit=60):
        self.speed_limit = speed_limit
        self.current_speed = 0
        self.weather_factor = 1.0
        self.safety_mode = False

    def set_safety_mode(self, enabled: bool):
        """Enable or disable safety mode. Safety mode enforces stricter limits."""
        self.safety_mode = enabled

    def update_speed(self, road_condition:str, traffic_density:int, slope_angle:int=0) -> float:
        """
        Adjusts speed based on:
          - road_condition: str ('clear', 'wet', 'icy')
          - traffic_density: int (0-100)
          - slope_angle: int (-10 to +10, downhill/uphill)
        Returns the new target speed rounded to two decimal places.
        Raises ValueError if any input is outside its valid range.
        """

        base_speed = self.speed_limit

        # Validate numeric ranges (Error Handling requirement).
        if not (0 <= traffic_density <= 100):
            raise ValueError("Invalid traffic density")
        if not (-10 <= slope_angle <= 10):
            raise ValueError("Invalid slope angle")

        # Adjust for road condition.
        if road_condition == 'wet':
            self.weather_factor = 0.85
        elif road_condition == 'icy':
            self.weather_factor = 0.6
        elif road_condition == 'clear':
            self.weather_factor = 1.0
        else:
            raise ValueError("Invalid road condition")

        base_speed *= self.weather_factor

        # Adjust for traffic density.
        if traffic_density >= 50:
            if traffic_density > 80:
                base_speed -= 20
            else:
                base_speed -= 10

        # Adjust for slope angle.
        if slope_angle > 0:  # uphill
            base_speed -= slope_angle
        elif slope_angle < 0:  # downhill
            base_speed += abs(slope_angle)

        # Safety mode clamping.
        if self.safety_mode:
            base_speed = min(base_speed, self.speed_limit - 10)
        else:
            base_speed = max(base_speed, 0)

        self.current_speed = base_speed
        return round(self.current_speed, 2)


"""
Data models for Minseo FestivalWeek Visit Planner.

Includes:
- Relative: stores location, district, preferred days, time windows, duration, bonus
- TransportMode: stores speed, cost, and transfer time
"""

class Relative:
    def __init__(
        self,
        name,
        latitude,
        longitude,
        preferred_days,
        preferred_window,
        happiness_bonus,
        district=None,
        duration=0
    ):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

        # Example: ["Mon", "Thu"]
        self.preferred_days = preferred_days

        # Example: ("18:00", "20:00")
        self.preferred_window = preferred_window

        # Happiness bonus for visiting
        self.happiness_bonus = happiness_bonus

        # District name (Gangnam-gu, Jongno-gu, etc.)
        self.district = district

        # Visit duration in minutes (45–90)
        self.duration = duration

        # These fields are filled by the scheduler
        self.arrival_time_str = None
        self.departure_time_str = None
        self.chosen_mode = None
        self.travel_minutes = 0
        self.travel_cost = 0
        self.travel_distance = 0

    def __repr__(self):
        return f"Relative({self.name}, {self.district})"


class TransportMode:
    def __init__(self, name, speed, cost_per_km, transfer_time):
        self.name = name
        self.speed = speed              # km/h
        self.cost_per_km = cost_per_km  # cost per km
        self.transfer_time = transfer_time  # minutes added when switching modes

    def __repr__(self):
        return f"TransportMode({self.name})"


"""
Utility functions for Minseo Festival–Week Visit Planner.

Includes:
- Haversine distance calculation (km)
- Time window checking
- General helper utilities
"""

from math import radians, sin, cos, sqrt, atan2
from datetime import time



# HAVERSINE DISTANCE (KM)

def haversine(lat1, lon1, lat2, lon2):
    """
    Compute the great-circle distance between two points on Earth (km).
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth radius in km

    lat1_r = radians(lat1)
    lon1_r = radians(lon1)
    lat2_r = radians(lat2)
    lon2_r = radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c



# TIME WINDOW CHECK

def within_time_window(arrival_time: time, start: time, end: time) -> bool:
    """
    Returns True if arrival_time is within [start, end].
    """
    return start <= arrival_time <= end



# CLAMP UTILITY

def clamp(value, min_val, max_val):
    """
    Restrict a value to the range [min_val, max_val].
    Useful for map scaling or normalization.
    """
    return max(min_val, min(value, max_val))

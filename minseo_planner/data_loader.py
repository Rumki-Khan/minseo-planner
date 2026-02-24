
"""
Data loading utilities for Minseo's visit planner.

This version uses package-relative paths so that CSV files
load correctly regardless of the working directory.
"""

import csv
import os
from minseo_planner.models import Relative, TransportMode


class DataLoader:
    def __init__(self):
        # Path to the directory containing this file
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the data folder inside the package
        self.data_dir = os.path.join(self.base_dir, "data")

    
    # Helper: Build full path to a data file
    
    def _full_path(self, filename):
        return os.path.join(self.data_dir, filename)

    
    # Load relatives

    def load_relatives(self, filename):
        filepath = self._full_path(filename)
        relatives = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    relatives.append(
                        Relative(
                            name=row["Relative"],
                            district=row["District"],
                            latitude=float(row["Lat"]),
                            longitude=float(row["Lon"]),
                            preferred_days=[d.strip() for d in row["PreferredDays"].split(",")],
                            preferred_window=tuple(row["PreferredTime"].split("-")),
                            happiness_bonus=float(row["Bonus"]),
                            duration=int(row["Duration"])
                        )
                    )
        except Exception as e:
            print(f"Error loading relatives from {filepath}: {e}")
            return []

        return relatives

    
    # Load transport modes

    def load_transport(self, filename):
        filepath = self._full_path(filename)
        modes = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    modes.append(
                        TransportMode(
                            name=row["Mode"],
                            speed=float(row["Speed"]),
                            cost_per_km=float(row["CostPerKm"]),
                            transfer_time=float(row["TransferTime"])
                        )
                    )
        except Exception as e:
            print(f"Error loading transport modes from {filepath}: {e}")
            return []

        return modes

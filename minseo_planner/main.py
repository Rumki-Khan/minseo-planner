# main.py
"""
Interactive CLI for Minseo's festival-week visit planner.

Features:
- Load data from CSV
- Generate best weekly schedule (50 random restarts)
- Change scoring weights (alpha, beta)
- Show last schedule and score
- Export schedule to file
- Basic error handling for menu + files
"""

import os
from minseo_planner.data_loader import DataLoader
from minseo_planner.scheduler import Scheduler


class Main:
    def __init__(self):
        self.data_loader = DataLoader()
        self.scheduler = Scheduler(preference="time", alpha=0.05, beta=0.02, restarts=50)

        self.relatives = []
        self.transport_modes = []

        self.last_schedule = None
        self.last_totals = None

    
    # DATA LOADING
   
    def load_data(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            rel_path = os.path.join(base_dir, "data", "relatives.csv")
            tr_path = os.path.join(base_dir, "data", "transport.csv")

            self.relatives = self.data_loader.load_relatives(rel_path)
            self.transport_modes = self.data_loader.load_transport(tr_path)

            print(f"Loaded relatives: {len(self.relatives)}")
            print(f"Loaded transport modes: {len(self.transport_modes)}")

        except FileNotFoundError as e:
            print(f"[ERROR] Missing data file: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")

    
    def generate_schedule(self):
        if not self.relatives or not self.transport_modes:
            print("[WARN] Data not loaded yet. Loading now...")
            self.load_data()

        if not self.relatives or not self.transport_modes:
            print("[ERROR] Cannot generate schedule without data.")
            return

        print("\nGenerating best weekly schedule (50 restarts)...")
        schedule_by_day, totals = self.scheduler.generate_best_schedule(
            self.relatives, self.transport_modes
        )

        self.last_schedule = schedule_by_day
        self.last_totals = totals

        text = self.scheduler.format_schedule(schedule_by_day, totals)
        print("\n" + text)

        # Save default schedule.txt
        try:
            with open("schedule.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print("\n[INFO] Schedule saved to schedule.txt")
        except Exception as e:
            print(f"[ERROR] Could not save schedule.txt: {e}")

        # Generate maps
        try:
            self.scheduler.plot_route_multi_day(schedule_by_day, save_path="route_map.png")
        except Exception as e:
            print(f"[ERROR] Could not generate route maps: {e}")

    def show_last_schedule(self):
        if not self.last_schedule or not self.last_totals:
            print("\n[INFO] No schedule generated yet.")
            return

        text = self.scheduler.format_schedule(self.last_schedule, self.last_totals)
        print("\n" + text)

    def change_scoring_weights(self):
        print("\nCurrent weights:")
        print(f"  alpha (time penalty): {self.scheduler.alpha}")
        print(f"  beta  (cost penalty): {self.scheduler.beta}")

        try:
            a = input("Enter new alpha (e.g., 0.05): ").strip()
            b = input("Enter new beta  (e.g., 0.02): ").strip()

            alpha = float(a)
            beta = float(b)

            self.scheduler.alpha = alpha
            self.scheduler.beta = beta

            print(f"[INFO] Updated weights: alpha={alpha}, beta={beta}")

        except ValueError:
            print("[ERROR] Invalid numeric input. Weights unchanged.")

    def export_schedule(self):
        if not self.last_schedule or not self.last_totals:
            print("\n[INFO] No schedule to export. Generate one first.")
            return

        filename = input("Enter filename to export (e.g., schedule_export.txt): ").strip()
        if not filename:
            print("[ERROR] Empty filename. Export cancelled.")
            return

        text = self.scheduler.format_schedule(self.last_schedule, self.last_totals)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[INFO] Schedule exported to {filename}")
        except Exception as e:
            print(f"[ERROR] Could not export schedule: {e}")

    
    # MENU LOOP
    
    def run(self):
        while True:
            print("\n=== Minseo Festival–Week Visit Planner ===")
            print("1. Generate Best Weekly Schedule")
            print("2. Show Last Schedule & Score")
            print("3. Change Scoring Weights (alpha, beta)")
            print("4. Export Last Schedule to File")
            print("5. Exit")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.generate_schedule()
            elif choice == "2":
                self.show_last_schedule()
            elif choice == "3":
                self.change_scoring_weights()
            elif choice == "4":
                self.export_schedule()
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("[ERROR] Invalid menu selection. Please choose 1–5.")


if __name__ == "__main__":
    Main().run()


"""

Implements:
- Random restarts (50)
- Random starting relative
- Minseo’s allowed hours
- Daily visit limits
- Preferred windows
- Meeting durations
- Travel time & cost
- Fatigue penalty
- Full scoring engine
- Best schedule selection
- Runtime logging (decorator)
- Regex validation
- Error handling
- Global axis limits for maps
"""

import random
from datetime import datetime, timedelta
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from minseo_planner.utils import haversine
from minseo_planner.models import Relative
from minseo_planner.scoring import ScoringEngine
from minseo_planner.decorators import measure_runtime

WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DAY_COLORS = {
    "Mon": "red",
    "Tue": "blue",
    "Wed": "green",
    "Thu": "purple",
    "Fri": "orange",
    "Sat": "brown",
    "Sun": "pink"
}

# Minseo’s allowed hours
ALLOWED_WEEKDAY_START = "18:00"
ALLOWED_WEEKDAY_END   = "21:00"
ALLOWED_WEEKEND_START = "10:00"
ALLOWED_WEEKEND_END   = "21:00"

# Daily visit limits
MAX_WEEKDAY_VISITS = 2
MAX_WEEKEND_VISITS = 3


class Scheduler:
    def __init__(self, preference="time", alpha=0.05, beta=0.02, restarts=50):
        self.preference = preference
        self.alpha = alpha
        self.beta = beta
        self.restarts = restarts

        self.graph = None
        self.best_schedule = None
        self.best_score = None
        self.best_totals = None

   
    # TIME HELPERS

    def parse_time(self, t):
        return datetime.strptime(t, "%H:%M").time()

    def combine(self, day, t):
        idx = WEEK_DAYS.index(day)
        base = datetime(2024, 1, 1) + timedelta(days=idx)
        return datetime.combine(base.date(), t)

   
    # MODE SELECTION RULES

    def select_modes_for_distance(self, dist, modes):
        out = []
        for m in modes:
            name = m.name.lower()
            if dist > 3 and name in ("bus", "train"):
                out.append(m)
            elif 1 <= dist <= 3 and name == "bicycle":
                out.append(m)
            elif dist < 1 and name == "walking":
                out.append(m)
        return out or list(modes)

   
    # TRAVEL STATS
    
    def travel_stats(self, r1, r2, mode):
        dist = haversine(r1.latitude, r1.longitude, r2.latitude, r2.longitude)
        hours = dist / mode.speed if mode.speed > 0 else 0
        minutes = hours * 60 + mode.transfer_time
        cost = dist * mode.cost_per_km
        return dist, minutes, cost

   
    # BUILD GRAPH
   

    def build_graph(self, relatives):
        G = nx.Graph()
        for r in relatives:
            G.add_node(r.name, obj=r)

        for i in range(len(relatives)):
            for j in range(i + 1, len(relatives)):
                a, b = relatives[i], relatives[j]
                dist = haversine(a.latitude, a.longitude, b.latitude, b.longitude)
                G.add_edge(a.name, b.name, distance_km=dist)

        self.graph = G

   
    # CHECK MINSEO’S ALLOWED HOURS

    def allowed_hours(self, day, arrival_time):
        if day in ("Sat", "Sun"):
            return ALLOWED_WEEKEND_START <= arrival_time <= ALLOWED_WEEKEND_END
        else:
            return ALLOWED_WEEKDAY_START <= arrival_time <= ALLOWED_WEEKDAY_END

    
    # GREEDY SCHEDULE FOR ONE RESTART

    def greedy_schedule(self, relatives, modes):
        schedule_by_day = {d: [] for d in WEEK_DAYS}
        remaining = relatives[:]  # global pool of unvisited relatives
    
        for day in WEEK_DAYS:
    
            # Filter relatives who prefer this day
            todays_relatives = [r for r in remaining if day in r.preferred_days]
            if not todays_relatives:
                continue
    
            # Determine allowed hours for this day
            if day in ("Sat", "Sun"):
                day_start = self.parse_time(ALLOWED_WEEKEND_START)
                day_end   = self.parse_time(ALLOWED_WEEKEND_END)
                max_visits = MAX_WEEKEND_VISITS
            else:
                day_start = self.parse_time(ALLOWED_WEEKDAY_START)
                day_end   = self.parse_time(ALLOWED_WEEKDAY_END)
                max_visits = MAX_WEEKDAY_VISITS
    
            # Pick a starting relative for this day
            start = random.choice(todays_relatives)
            current = start
            current_dt = self.combine(day, day_start)
    
            # Add first visit
            depart_dt = current_dt + timedelta(minutes=current.duration)
            schedule_by_day[day].append({
                "name": current.name,
                "district": current.district,
                "lat": current.latitude,
                "lon": current.longitude,
                "arrival": current_dt.time().strftime("%H:%M"),
                "departure": depart_dt.time().strftime("%H:%M"),
                "mode": "Start",
                "distance": 0,
                "travel_time": 0,
                "cost": 0
            })
    
            current_dt = depart_dt
            remaining.remove(start)
    
            # Continue scheduling for THIS day only
            while len(schedule_by_day[day]) < max_visits:
    
                best_choice = None
                best_metric = None
    
                for cand in remaining:
                    if day not in cand.preferred_days:
                        continue
    
                    # Travel stats
                    dist = self.graph[current.name][cand.name]["distance_km"]
                    allowed_modes = self.select_modes_for_distance(dist, modes)
    
                    for mode in allowed_modes:
                        dist_km, travel_min, cost = self.travel_stats(current, cand, mode)
                        arrival_dt = current_dt + timedelta(minutes=travel_min)
                        arrival_t = arrival_dt.time()
    
                        # Check allowed hours
                        if not (day_start <= arrival_t <= day_end):
                            continue
    
                        # Check preferred window
                        pref_start = self.parse_time(cand.preferred_window[0])
                        pref_end   = self.parse_time(cand.preferred_window[1])
                        if not (pref_start <= arrival_t <= pref_end):
                            continue
    
                        depart_dt = arrival_dt + timedelta(minutes=cand.duration)
                        depart_t = depart_dt.time()
    
                        # Check departure still within allowed hours
                        if not (day_start <= depart_t <= day_end):
                            continue
    
                        # Preference metric
                        metric = travel_min if self.preference == "time" else cost
    
                        if best_metric is None or metric < best_metric:
                            best_metric = metric
                            best_choice = (cand, arrival_dt, depart_dt, mode, dist_km, travel_min, cost)
    
                if best_choice is None:
                    break
    
                cand, arrival_dt, depart_dt, mode, dist_km, travel_min, cost = best_choice
    
                schedule_by_day[day].append({
                    "name": cand.name,
                    "district": cand.district,
                    "lat": cand.latitude,
                    "lon": cand.longitude,
                    "arrival": arrival_dt.time().strftime("%H:%M"),
                    "departure": depart_dt.time().strftime("%H:%M"),
                    "mode": mode.name,
                    "distance": dist_km,
                    "travel_time": travel_min,
                    "cost": cost
                })
    
                current = cand
                current_dt = depart_dt
                remaining.remove(cand)
    
        return schedule_by_day


    # MAIN ENTRY: RUN 50 RESTARTS AND PICK BEST

    @measure_runtime
    def generate_best_schedule(self, relatives, modes):
        self.build_graph(relatives)
        scorer = ScoringEngine(alpha=self.alpha, beta=self.beta)

        best_score = None
        best_schedule = None
        best_totals = None

        for _ in range(self.restarts):
            random.shuffle(relatives)
            schedule = self.greedy_schedule(relatives, modes)
            totals = scorer.compute_total_score(schedule, relatives)
            score = totals["final_score"]

            if best_score is None or score > best_score:
                best_score = score
                best_schedule = schedule
                best_totals = totals

        self.best_schedule = best_schedule
        self.best_score = best_score
        self.best_totals = best_totals

        return best_schedule, best_totals

    
    # FORMATTING SCHEDULE

    def format_schedule(self, schedule_by_day, totals):
        lines = []
        lines.append("=== Best Weekly Schedule ===\n")

        for day in WEEK_DAYS:
            if not schedule_by_day[day]:
                continue

            lines.append(f"Day {day}")
            for r in schedule_by_day[day]:
                lines.append(
                    f"  {r['name']} ({r['arrival']}–{r['departure']})\n"
                    f"    District: {r['district']}\n"
                    f"    Mode: {r['mode']}\n"
                    f"    Distance: {r['distance']:.2f} km\n"
                    f"    Travel Time: {r['travel_time']:.1f} min\n"
                    f"    Cost: {r['cost']:.2f}\n"
                )

        lines.append("\n=== Totals ===")
        lines.append(f"Total Happiness Bonus: {totals['bonus']:.2f}")
        lines.append(f"Total Travel Minutes: {totals['minutes']:.2f}")
        lines.append(f"Total Travel Cost: {totals['cost']:.2f}")
        lines.append(f"Fatigue Penalty: {totals['fatigue']}")
        lines.append(f"Final Score: {totals['final_score']:.2f}")

        return "\n".join(lines)


    # MAP VISUALIZATION (GLOBAL AXIS LIMITS)

    def plot_route_multi_day(self, schedule_by_day, save_path="route_map.png"):
        # Collect global bounds
        all_lats = []
        all_lons = []

        for day, visits in schedule_by_day.items():
            for r in visits:
                all_lats.append(r["lat"])
                all_lons.append(r["lon"])

        min_lat = min(all_lats) - 0.01
        max_lat = max(all_lats) + 0.01
        min_lon = min(all_lons) - 0.01
        max_lon = max(all_lons) + 0.01

        # Combined map
        plt.figure(figsize=(12, 10))

        for day, visits in schedule_by_day.items():
            for r in visits:
                plt.scatter(r["lon"], r["lat"], color="black", s=50)
                label = f"{r['name']}\nArr: {r['arrival']}\nDep: {r['departure']}"
                plt.text(r["lon"] + 0.001, r["lat"] + 0.001, label, fontsize=8)

        for day, visits in schedule_by_day.items():
            if len(visits) < 2:
                continue

            color = DAY_COLORS[day]

            for i in range(1, len(visits)):
                prev = visits[i - 1]
                curr = visits[i]

                plt.plot(
                    [prev["lon"], curr["lon"]],
                    [prev["lat"], curr["lat"]],
                    color=color,
                    linewidth=2
                )

        plt.xlim(min_lon, max_lon)
        plt.ylim(min_lat, max_lat)
        plt.title("Multi-Day Optimized Route Map")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"Combined map saved: {save_path}")

        # Per-day maps
        for day, visits in schedule_by_day.items():
            if not visits:
                continue

            plt.figure(figsize=(10, 8))

            for r in visits:
                plt.scatter(r["lon"], r["lat"], color="black", s=50)
                label = f"{r['name']}\nArr: {r['arrival']}\nDep: {r['departure']}"
                plt.text(r["lon"] + 0.001, r["lat"] + 0.001, label, fontsize=8)

            for i in range(1, len(visits)):
                prev = visits[i - 1]
                curr = visits[i]

                plt.plot(
                    [prev["lon"], curr["lon"]],
                    [prev["lat"], curr["lat"]],
                    color=DAY_COLORS[day],
                    linewidth=2
                )

            plt.xlim(min_lon, max_lon)
            plt.ylim(min_lat, max_lat)
            plt.title(f"Route Map — {day}")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.grid(True)
            plt.tight_layout()

            day_path = save_path.replace(".png", f"_{day}.png")
            plt.savefig(day_path, dpi=300)
            plt.close()

            print(f"Day map saved: {day_path}")

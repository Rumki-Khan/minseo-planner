"""
Scoring engine for Minseo's festival-week visit planner.

Implements:
- Full or half happiness bonus
- Travel time penalty (alpha)
- Travel cost penalty (beta)
- Weekend fatigue penalty
- Regex validation for HH:MM time format
"""

import re


class ScoringEngine:
    def __init__(self, alpha=0.05, beta=0.02):
        """
        alpha: penalty per travel minute
        beta: penalty per travel cost unit
        """
        self.alpha = alpha
        self.beta = beta

    
    # TIME VALIDATION (REGEX)


    def validate_time(self, t):
        """Validate HH:MM format using regex."""
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", t):
            raise ValueError(f"Invalid time format: {t}")

    
    # HAPPINESS BONUS
    

    def compute_visit_score(self, visit, relative):
        """
        Full bonus if:
            - visit day is in preferred days
            - arrival time is within preferred window
        Otherwise:
            - half bonus
        """
        start = visit["arrival"]
        self.validate_time(start)

        day = visit["day"]
        start_time = start

        preferred_days = relative.preferred_days
        pref_start, pref_end = relative.preferred_window

        if (day in preferred_days) and (pref_start <= start_time <= pref_end):
            return relative.happiness_bonus
        else:
            return relative.happiness_bonus * 0.5

    
    # FATIGUE PENALTY
    

    def compute_fatigue_penalty(self, schedule_by_day):
        """
        -2 points for each weekend day (Sat, Sun) with 3 visits.
        """
        penalty = 0
        for day, visits in schedule_by_day.items():
            if day in ("Sat", "Sun") and len(visits) == 3:
                penalty -= 2
        return penalty

    
    # TOTAL SCORE
    

    def compute_total_score(self, schedule_by_day, relatives):
        """
        Computes:
        - Total happiness bonus
        - Total travel minutes
        - Total travel cost
        - Fatigue penalty
        - Final score
        """
        total_bonus = 0
        total_minutes = 0
        total_cost = 0

        # Map name → relative object
        rel_map = {r.name: r for r in relatives}

        for day, visits in schedule_by_day.items():
            for v in visits:
                r = rel_map[v["name"]]
                v["day"] = day  # add day for scoring

                # Happiness
                total_bonus += self.compute_visit_score(v, r)

                # Travel + meeting duration
                total_minutes += v["travel_time"] + r.duration

                # Cost
                total_cost += v["cost"]

        # Fatigue
        fatigue = self.compute_fatigue_penalty(schedule_by_day)

        # Final score (matches exam description)
        score = (
            total_bonus
            - self.alpha * total_minutes
            - self.beta * total_cost
            + fatigue  # fatigue is negative when applied
        )

        return {
            "bonus": total_bonus,
            "minutes": total_minutes,
            "cost": total_cost,
            "fatigue": fatigue,
            "final_score": score
        }

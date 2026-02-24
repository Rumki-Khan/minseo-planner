
"""
Metaprogramming utilities for Minseo's visit planner.

Includes:
- measure_runtime: logs execution time of functions
- log_call: logs when a function is called
"""

import time
import functools


def measure_runtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start

        # Print to console
        print(f"[LOG] {func.__name__} completed in {elapsed:.4f} seconds")

        # Write runtime log file
        try:
            restarts = getattr(args[0], "restarts", "N/A")
            write_runtime_log(func.__name__, elapsed, restarts)
        except Exception:
            pass

        return result
    return wrapper



def write_runtime_log(func_name, elapsed, restarts):
    with open("runtime_log.txt", "w", encoding="utf-8") as f:
        f.write("=== Runtime Log ===\n\n")
        f.write(f"Function: {func_name}\n")
        f.write(f"Total candidate schedules evaluated: {restarts}\n")
        f.write(f"Execution time: {elapsed:.4f} seconds\n")


def log_call(func):
    """
    Decorator that logs when a function is called.

    Useful for debugging or tracing program flow.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


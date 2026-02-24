
"""
Console entry point for Minseo's festival-week visit planner.

This module allows the package to expose a command-line tool
called `minseo-planner` via setup.py.
"""

from minseo_planner.main import Main


def run():
    """Entry point for the console script."""
    app = Main()
    app.run()


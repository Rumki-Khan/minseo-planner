# Minseo Festival Week Visit Planner

A modular Python application that generates an optimized weekly visit schedule for Minseo during the festival week. The system balances **happiness**, **travel time**, **travel cost**, and **fatigue**, producing a high‑quality weekly plan using a rule‑based greedy scheduling algorithm.


---

##  Overview

Minseo wants to visit ten relatives across Seoul during the festival week. Each relative has:

- A preferred district  
- A preferred day and time  
- A visit duration  
- A happiness bonus  

The planner computes:

- Travel distances  
- Travel times  
- Travel costs  
- Daily schedules  
- Weekly schedules  
- Final score (happiness – penalties)

The system outputs:

- A complete weekly schedule  
- Route maps (daily + multi‑day)  
- A timetable visualization  
- A runtime log  
- A final score summary  

---

##  Architecture

The system follows **clean modular design**:

- **DataLoader** — loads CSV data and validates formats  
- **Scheduler** — computes distances, selects transport modes, builds schedules  
- **Scoring** — calculates happiness, penalties, and final score  
- **Utils** — helper functions (Haversine, time parsing, conversions)  
- **CLI** — user interface for generating schedules and exporting results  

A full UML diagram is included in the report.

---

## 📂 Project Structure

minseo_planner/
│
├── cli.py
├── main.py
├── scheduler.py
├── scoring.py
├── data_loader.py
├── models.py
├── utils.py
├── decorators.py
├── exceptions.py
│
├── data/
│   ├── relatives.csv
│   └── transport.csv
│
├── output/
│   ├── schedule.txt
│   ├── runtime_log.txt
│   ├── route_map_mon.png
│   ├── route_map_multi.png
│   └── ...
│
├── tests/
│   └── test_planner.py
│
├── clean.sh
├── requirements.txt
└── README.md
└── setup.py


---

##  Installation

### 1. Clone the repository


git clone (https://github.com/Rumki-Khan/minseo-planner)

cd minseo-planner

### 2. Create and activate a virtual environment

python3 -m venv venv

source venv/bin/activate   # macOS/Linux

venv\Scripts\activate      # Windows

### 3. Install dependencies

pip install -r requirements.txt

## 4. Install the package locally

pip install .

## Usage
Run the CLI: minseo-planner

You will see a menu with options:

Generate weekly schedule

Show last schedule

Change scoring weights

Export schedule

Exit

All outputs are saved in the output/ directory.

### How the Algorithm Works

1. Data Loading
    Reads CSV files

    Validates time formats using regex

    Converts rows into dataclasses

2. Scheduling
    For each day:

    Filter relatives available that day

    Compute:

    Distance (Haversine)

    Travel time

    Travel cost

    Happiness

    Select the best candidate using a greedy strategy

    Apply fatigue penalties for long days

3. Scoring
    The final score is:

    Final Score = Happiness − α·TravelMinutes − β·TravelCost − FatiguePenalty
    
    Default weights:
    α = 0.05
    β = 0.02

### Visual Outputs

The system generates:

Daily route maps

Multi‑day route map

Timetable visualization

Schedule summary

Runtime log

All images and logs are saved automatically.

### Testing

Run all tests:

pytest

### Cleanup
A cleanup script is included:

./clean.sh

This removes:

__pycache__

.pyc files

LaTeX build files

Generic cache folders

### Assumptions & Limitations

Uses straight‑line (Haversine) distance

Transport mode selection is rule‑based

Greedy algorithm may not find the global optimum

Visit durations are fixed

No traffic modelling

## Requirements

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Required Python libraries:
  - pandas
  - numpy
  - matplotlib
  - geopy
  - tabulate
  - networkx (for visual)
  - pytest (for testing)
- CSV data files:
  - relatives.csv
  - transport.csv
- Operating System:
  - Linux, macOS, or Windows





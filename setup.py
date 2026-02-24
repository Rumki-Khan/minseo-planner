import setuptools

setuptools.setup(
    name="minseo-planner",
    version="1.0.0",
    description="Minseo's festival week visit planner",
    author="Rumman",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "networkx",
        "matplotlib",
        "pandas",
        "numpy",
        "geopy",
        "tabulate",
        "pytest",
        "setuptools"
    ],
    entry_points={
        "console_scripts": [
            "minseo-planner = minseo_planner.cli:run"
        ]
    },
    package_data={
        "minseo_planner": ["data/*.csv"]
    },
)

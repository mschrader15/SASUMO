import os


TEMP_PATTERN = "__temp__"
SUMO_HOME = os.environ.get("SUMO_HOME")

SEED = 1e6
PROBLEM_DESCRIPT_FILE_NAME = "SALib_Problem.json"
SAMPLES_FILE_NAME = "SALib_Samples.txt"
RESULTS_NAME = "output.txt"
SOBOL_ANALYSIS = lambda x: f"sobol_analysis_{x}.csv"

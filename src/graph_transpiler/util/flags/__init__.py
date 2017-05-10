import os

from graph_transpiler.util.flags import optimize

DEBUG = os.environ.get("DEBUG", "0") == "1"
VISUALIZE_MEMORY_ALLOCATION = os.environ.get("VISUALIZE_MEMORY_ALLOCATION", "0") == "1"

import os

from webdnn.util.flags import optimize
from webdnn.util.flags import test

DEBUG = os.environ.get("DEBUG", "0") == "1"
VISUALIZE_MEMORY_ALLOCATION = os.environ.get("VISUALIZE_MEMORY_ALLOCATION", "0") == "1"

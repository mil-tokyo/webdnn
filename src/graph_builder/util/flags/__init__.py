import os
from graph_builder.util.flags import optimize
from graph_builder.util.flags import backend

DEBUG = os.environ.get("DEBUG", "0") == "1"

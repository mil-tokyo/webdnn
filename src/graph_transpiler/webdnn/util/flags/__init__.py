import os

from webdnn.util.flags import optimize
from webdnn.util.flags import test

DEBUG = os.environ.get("DEBUG", "0") == "1"
VISUALIZE_MEMORY_ALLOCATION = os.environ.get("VISUALIZE_MEMORY_ALLOCATION", "0") == "1"
AGGRESSIVE_ORDER_INFERENCE = os.environ.get("AGGRESSIVE_ORDER_INFERENCE", "1") == "1"
AUTO_UPGRADE_OPERATOR_TYPE = os.environ.get("AUTO_UPGRADE_OPERATOR_TYPE", "1") == "1"

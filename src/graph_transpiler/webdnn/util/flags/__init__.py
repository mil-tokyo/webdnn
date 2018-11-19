import os

from webdnn.util.flags import optimize
from webdnn.util.flags import test

DEBUG = os.environ.get("DEBUG", "0") == "1"
VISUALIZE_MEMORY_ALLOCATION = os.environ.get("VISUALIZE_MEMORY_ALLOCATION", "0") == "1"
AUTO_UPGRADE_OPERATOR_TYPE = os.environ.get("AUTO_UPGRADE_OPERATOR_TYPE", "1") == "1"
# Worker thread is generated to avoid stack overflow. Turn off by setting this option.
NO_WORKER_THREAD = os.environ.get("NO_WORKER_THREAD", "0") == "1"

# If True, type assertion always raise exceptions if it failed.
FORCE_TYPE_CHECK = os.environ.get("FORCE_TYPE_CHECK", "0") == "1"

import sys

if sys.version_info < (3, 6):
    sys.stderr.write("Sorry, this library only works with python >= 3.6\n")
    sys.exit(1)

import json
from setuptools import setup, find_packages

with open("./package.json") as f:
    version = json.load(f)["version"]

setup(
    name="webdnn",
    version=version,
    package_dir={"": "src/graph_transpiler"},
    packages=find_packages("src/graph_transpiler"),
    package_data={"": "*.js"}
)

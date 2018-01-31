import sys

if sys.version_info < (3, 6):
    sys.stderr.write("Sorry, this library only works with python >= 3.6\n")
    sys.exit(1)

import json
from setuptools import setup, find_packages

with open("./package.json") as f:
    package_info = json.load(f)

setup(
    name="webdnn",
    version=package_info["version"],
    python_requires=">=3.6",
    package_dir={"": "src/graph_transpiler"},
    packages=find_packages("src/graph_transpiler"),
    package_data={"": "*.js"}, install_requires=['numpy'],
    url="https://github.com/mil-tokyo/webdnn",
    description=package_info["description"],
    author=package_info["author"]["name"],
    author_email=package_info["author"]["email"],
    keywords=" ".join(package_info["keywords"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6"
        ]
)

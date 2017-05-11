from setuptools import setup, find_packages

setup(
    name="graph_transpiler",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages("src")
)

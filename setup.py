from setuptools import setup, find_packages

setup(
    name="webdnn",
    version="1.1.0",
    package_dir={"": "src/graph_transpiler"},
    packages=find_packages("src/graph_transpiler"),
    package_data={"": "*.js"}
)

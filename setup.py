from setuptools import setup, find_packages

setup(
    name="webdnn",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={"": "*.js"}
)

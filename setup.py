import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="function-ext-monitor",
    version="0.0.3",
    description="This package provides a decorator to wrap around a function so that a report is sent to external server every time function runs.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sopherapps/function-ext-monitor",
    author="Martin Ahindura",
    author_email="team.sopherapps@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("test",)),
    include_package_data=True,
    install_requires=["requests"],
    entry_points={
    },
)

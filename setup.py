""" Setup file. """

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    README = readme_file.read()

exec(open("src/matching/version.py", "r").read())

setup(
    name="pairing",
    version=__version__,
    description="A package to match mentors to mentees.",
    long_description=README,
    url="https://github.com/ophie200/pairing",
    author="Nancy Wong",
    author_email="nawong@mozilla.com",
    license="MIT",
    keywords=["pairing matching mentor-mentee preference"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    tests_require=["pytest", "numpy"],
)
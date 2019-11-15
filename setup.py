# setup.py
# Author: Thomas MINIER - MIT License 2019
from setuptools import setup, find_packages

__version__ = "0.0.1"

with open('README.rst') as file:
    long_description = file.read()

with open('requirements.txt') as file:
    install_requires = file.read().splitlines()

setup(
    name="ottr",
    version=__version__,
    author="Thomas Minier",
    author_email="thomas.minier@univ-nantes.fr",
    url="https://github.com/Callidon/pyOTTR",
    description="Manipulate OTTR Reasonable Ontology Templates in Python",
    long_description=long_description,
    keywords=["rdf", "owl", "ottr", "template", "ontology", "reusable"],
    license="MIT",
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(exclude=["tests", "tests.*"])
)

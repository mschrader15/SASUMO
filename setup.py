"""
This was taken almost verbatim (besides package name and info) from FLOW

https://github.com/flow-project/flow/blob/master/setup.py
"""

from os.path import dirname, realpath
from setuptools import find_packages, setup, Distribution


def _read_requirements_file():
    """Return the elements in requirements.txt."""
    req_file_path = f'{dirname(realpath(__file__))}/requirements.txt'
    with open(req_file_path) as f:
        return [line.strip() for line in f]


class BinaryDistribution(Distribution):
    """See parent class."""

    def has_ext_modules(self):
        """Return True for external modules."""
        return True


setup(
    name='SASUMO',
    version="0.0.2",
    distclass=BinaryDistribution,
    packages=find_packages(),
    description=("SASUMO - Sensitivity Analysis"),
    long_description=open("README.md").read(),
    url="https://github.com/mschrader15/SASUMO",
    keywords=("autonomous vehicles intelligent-traffic-control"
              "reinforcement-learning deep-learning python"
              "sensitivity-analysis uncertianty-analysis"),
    install_requires=_read_requirements_file(),
    zip_safe=False,
)
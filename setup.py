# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


install_requirements = [
    "qat-comm",
    "qat-core",
    "qat-lang",
    "typing",
    "numpy>=1.15",
]

tests_requirements = [
        "parameterized",
        "sympy",
]

setup(
    name="Quantum-Circuit-Binary-Field-Montgomery-Multiplication-Modular-Exponentiation",
    version="0.1.0",
    description="A Quantum Circuit to calculate Montgomery multiplication based on modular exponentiation algorithm",
    url="https://github.com/lipidex/Quantum-Circuit-Binary-Field-Montgomery-Multiplication-Modular-Exponentiation",
    author="lipidex",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    keywords="qat atos quantum qlm",
    packages=find_packages(exclude=['test*', 'experiments*']),
    install_requires=install_requirements,
    tests_requires=tests_requirements,
    test_suite="unittest",
    include_package_data=True,
    python_requires=">=3.9,<3.10",
)
# setup.py
from setuptools import setup, find_packages

setup(
    name="MemBrainPy",
    version="0.1.1",
    author="Guillermo Sanchis Terol",
    author_email="guillesanchisterol@gmail.com",
    description="Librería para realizar computación con membranas",
    url="https://github.com/Guillemon01/MemBrainPy",
    packages=find_packages(),        # detecta MemBrainPy y subpaquetes
    install_requires=[
        "pandas>=1.0",
        "matplotlib>=3.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

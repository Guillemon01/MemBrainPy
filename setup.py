
from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

# Lee el README.md
long_descr = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="MemBrainPy",
    version="0.1.4",
    author="Guillermo Sanchis Terol",
    author_email="guillesanchisterol@gmail.com",
    description="Librería para realizar computación con membranas",
    long_description=long_descr,
    long_description_content_type="text/markdown",
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

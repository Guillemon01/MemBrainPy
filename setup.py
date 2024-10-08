# setup.py
from setuptools import setup, find_packages

setup(
    name="MemBrainPy",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # Aquí puedes añadir dependencias si las tienes
    author="Guillermo Sanchis Terol",
    author_email="guillesanchisterol@gmail.com",
    description="Librería para realizar computación con membranas",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Guillemon01/MemBrainPy",  # URL de tu proyecto
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

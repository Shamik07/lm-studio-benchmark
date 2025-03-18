#!/usr/bin/env python3
"""
Setup script for the LM Studio Coding Benchmark tool.
"""

from setuptools import setup, find_packages

setup(
    name="lm-studio-benchmark",
    version="1.0.0",
    description="A comprehensive tool for benchmarking LM Studio models on coding tasks",
    author="LM Studio",
    packages=find_packages(),
    install_requires=[
        "requests",
        "matplotlib",
        "numpy",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "lm-benchmark=benchmark_runner:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
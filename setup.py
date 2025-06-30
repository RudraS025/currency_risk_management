"""
Setup script for Currency Risk Management System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="currency-risk-management",
    version="1.0.0",
    author="Currency Risk Management Team",
    author_email="contact@example.com",
    description="A comprehensive software solution for managing currency risk in international trade transactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/currency-risk-management",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "viz": [
            "kaleido>=0.2.1",  # For saving plotly charts as images
        ]
    },
    entry_points={
        "console_scripts": [
            "currency-risk=currency_risk_mgmt.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

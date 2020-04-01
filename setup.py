from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="nba_parser",
    packages=["nba_parser"],
    version="0.2",
    license="GNU General Public License v3.0",
    description="python package to clean up ETL functions using nba_scraper output as input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcbarlowe/nba_parser",
    author="Matthew Barlowe",
    author_email="matt@barloweanalytics.com",
    keywords=["basketball", "NBA"],
    install_requires=["pandas", "numpy", "sklearn"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
    ],
)

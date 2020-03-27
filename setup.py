from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="nba_parser",
    packages=["nba_scraper"],
    version="0.0.1",
    license="GNU General Public License v3.0",
    description="python package to clean up ETL functions using nba_scraper output as input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Barlowe",
    author_email="matt@barloweanalytics.com",
    keywords=["basketball", "NBA"],
    install_requires=["pandas", "numpy"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
    ],
)

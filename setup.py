#!/usr/bin/env python
"""Install minimal requirements."""
import os

from setuptools import find_packages, setup

from review import __doc__ as project_short_desc
from review import __version__ as project_version


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def _read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if __name__ == "__main__":
    setup(
        name="re-view",
        version=project_version,
        author="William Quelho Ferreira",
        author_email="wqferr@gmail.com",
        description=project_short_desc,
        license="GPLv3",
        keywords="regex visualization tool debug",
        url="https://github.com/wqferr/re-view",
        packages=find_packages(),
        entry_points={"console_scripts": ["review=review.app:main"]},
        long_description=_read("README.md"),
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3 :: Only",
        ],
        install_requires=["blessed>=1.16", "lorem>=0.1.1"],
    )

#!/usr/bin/python
import sys
sys.path.append('weebl/')
import weebl
from setuptools import setup, find_packages


setup(
    name="weebl",
    version=weebl.__version__,
    description="Web App for OIL",
    author="Darren Hoyland",
    author_email="<darren.hoyland@canonical.com>",
    url="http://launchpad.net/weebl",
    package_dir={'': 'weebl'},
    packages=find_packages('weebl'),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python3",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"],
    entry_points={
        "console_scripts": [
            'weebl_setup = set_up_new_environment:main',
        ]
    },
    data_files=[
        ('/usr/share/weebl',
            ['contrib/weebl-nginx-site.conf'])
    ],
)

#!/usr/bin/python
import weebl
from setuptools import setup, find_packages


setup(
    name="weebl",
    version=weebl.__version__,
    description="Web App for OIL",
    author="Darren Hoyland",
    author_email="<darren.hoyland@canonical.com>",
    url="http://launchpad.net/weebl",
    packages=find_packages(exclude=['weeblclient*']),
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

#!/usr/bin/env python3

"""
Copyright (c) 2019 Peter Leese

Licensed under the GPL License. See LICENSE file in the project root for full license information.  
"""

from distutils.core import setup

setup(
    name='Test Toolkit',
    version='1.0',
    description="Yet another python test toolkit",
    url='https://github.com/peter1010/test_toolkit',
    author='Peter1010',
    author_email='peter1010@localnet',
    license='GPL',
    package_dir={'test_toolkit': 'toolkit'},
    packages=['test_toolkit'],
    data_files=[],
)

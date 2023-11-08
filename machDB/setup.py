"""
 * Copyright of this product 2013-2023,
 * Machbase Corporation(or Inc.) or its subsidiaries.
 * All Rights reserved.
"""
#coding=utf8

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(
    name='machbaseAPI',
    version='1.1',
    description='Machbase-Python3-API',
    long_description='Python3 module for Machbase',
    url='http://www.machbase.com',
    author='machbase',
    author_email='support@machbase.com',
    platforms='WINDOWS',
    packages=['machbaseAPI'],
    data_files=[(get_python_lib()+'/machbaseAPI',['machbaseAPI.dll']),]
)

#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Epubzilla',
    version='0.1.1',
    author='Nicholas O\'Deegan',
    author_email='odeegan@gmail.com',
    packages=['epubzilla', 'epubzilla.test'],
    url='http://epubzilla.odeegan.com',
    license='LICENSE.txt',
    description='a library for extracting data from EPUB files',
    long_description=open('README.txt').read(),
    install_requires='lxml >= 2.3.5',
)

# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import (
    find_packages,
    setup
)

# TODO: [TD0008] Simplify installation.
# TODO: [TD0008] Add support for 'pip' or similar package manager.

# Access attributes without importing the file.
# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
ABSPATH_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
projectmeta = dict()
with open(os.path.realpath(os.path.join(
        ABSPATH_THIS_DIR, 'autonameow', 'core', 'version.py'
))) as fp:
    exec(fp.read(), projectmeta)


setup(
    name=projectmeta['__title__'],
    version=projectmeta['__version__'],
    author=projectmeta['__author__'],
    author_email=projectmeta['__email__'],
    maintainer=projectmeta['__author__'],
    maintainer_email=projectmeta['__email__'],
    description='Automagic File Renamer',
    keywords='automagic filename management metadata pim rename',
    url=projectmeta['__url_repo__'],
    license=projectmeta['__license__'],
    packages=find_packages(exclude=['unit']),
    package_data={
        'autonameow': [
            'extractors/metadata/pandoc_template.plain',
            'util/mimemagic.mappings',
        ],
    },
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'beautifulsoup4==4.4.1',
        'colorama==0.3.7',
        'chardet==2.3.0',
        'EbookLib==0.16',
        'guessit==2.1.0',
        'hypothesis==3.38.0',
        'isbnlib==3.5.6',
        'Pillow==3.1.2',
        'prompt-toolkit==1.0.15',
        'pytz==2014.10',
        'PyYAML==3.11',
        'Unidecode==0.4.19',
        'guessit==2.1.0',
        # NOTE: Run 'apt install python3-magic' on Debian-derivatives to satisfy the magic dependency.
        # 'python3-magic',   TODO: Which version is actually used??
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'autonameow = main:cli_main',
            'meowxtract = extract:cli_main',
        ]
    }
)

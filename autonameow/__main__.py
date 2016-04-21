#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Allow user to run Autonameow as a module from a directory or zip file.
"""

# Execute with:
# $ python autonameow/__main__.py (2.6)
# $ python -m autonameow          (2.7+)

import sys

from main import Autonameow

if __package__ is None and not hasattr(sys, "frozen"):
    # It is a direct call to __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
    autonameow = Autonameow()
    autonameow.main()

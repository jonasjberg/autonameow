# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016-2017, Jonas Sjoberg.

import argparse
from unittest import TestCase

from core import options


class TestArgumentValidators(TestCase):
    def test_arg_is_year_raises_exception(self):
        invalid_years = ['abc', '00', '', '19 00', ' ', None, '¡@$!']
        for y in invalid_years:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                options.arg_is_year(y)
            self.assertIsNotNone(e)
            # self.assertIn('"{}" is not a valid year'.format(y), e.exception)

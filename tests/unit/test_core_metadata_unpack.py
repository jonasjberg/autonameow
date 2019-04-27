# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from unittest import expectedFailure, TestCase

from core.metadata.unpack import split_title_subtitle


class TestSplitTitleSubtitle(TestCase):
    def _assert_splits(self, full_title, title, subtitle):
        actual_title, actual_subtitle = split_title_subtitle(full_title)
        self.assertEqual(title, actual_title)
        self.assertEqual(subtitle, actual_subtitle)

    def test_handles_empty_titles(self):
        self._assert_splits('', '', '')

    def test_handles_trivial_titles(self):
        self._assert_splits('foo', title='foo', subtitle='')
        self._assert_splits('foo bar', title='foo bar', subtitle='')

    def test_splits_title_with_subtitle_separated_by_single_semicolon(self):
        for given_title in [
            'Practical Meow with Gibson ; Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson ;Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson; Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson;Unleash the power of Meowing and unlock your creativity',
        ]:
            self._assert_splits(
                given_title,
                title='Practical Meow with Gibson',
                subtitle='Unleash the power of Meowing and unlock your creativity'
            )

    def test_splits_title_with_subtitle_separated_by_single_colon(self):
        for given_title in [
            'Practical Meow with Gibson : Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson :Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson: Unleash the power of Meowing and unlock your creativity',
            'Practical Meow with Gibson:Unleash the power of Meowing and unlock your creativity',
        ]:
            self._assert_splits(
                given_title,
                title='Practical Meow with Gibson',
                subtitle='Unleash the power of Meowing and unlock your creativity'
            )

    def test_splits_title_with_subtitle_separated_by_single_dash(self):
        for given_title in [
            'X Essentials - Programming the X Framework',
            'X Essentials -Programming the X Framework',
            'X Essentials- Programming the X Framework',
            'X Essentials-Programming the X Framework',
        ]:
            self._assert_splits(
                given_title,
                title='X Essentials',
                subtitle='Programming the X Framework'
            )

    def test_splits_full_title_containing_two_possible_separators(self):
        self._assert_splits(
            'Meowing for Computations - MEOW: A Gentle Introduction to Numerical Simulation with Gibson',
            title='Meowing for Computations - MEOW',
            subtitle='A Gentle Introduction to Numerical Simulation with Gibson'
        )
        self._assert_splits(
            'Programming the KIBBLE micro:bit: Getting Started with MicroFoodz',
            title='Programming the KIBBLE micro:bit',
            subtitle='Getting Started with MicroFoodz'
        )

    @expectedFailure
    def test_splits_full_title_containing_multiple_possible_separators(self):
        self._assert_splits(
            'Beginning MEOW Pets: From Novice To Professional ; [The Complete Guide To MEOW Pets - Everything You Need To Get Up And Running ; Included DVD Contains Full Version Of MEOW 9.1 Professional Edition]',
            title='Beginning MEOW Pets',
            # TODO: Maybe allow multiple subtitles, stored in a list?
            # subtitle='From Novice To Professional ; [The Complete Guide To MEOW Pets - Everything You Need To Get Up And Running ; Included DVD Contains Full Version Of MEOW 9.1 Professional Edition]'
            subtitle='From Novice To Professional'
        )

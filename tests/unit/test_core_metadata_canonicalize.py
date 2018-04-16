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

from unittest import TestCase

import unit.utils as uu
from core.metadata.canonicalize import (
    canonicalize_publisher,
    StringValueCanonicalizer
)


def _canonicalize_publisher(given):
    return canonicalize_publisher(given)


def _get_string_value_canonicalizer(*args, **kwargs):
    return StringValueCanonicalizer(*args, **kwargs)


PUBLISHER_CANONICAL_EQUIVALENTS = {
    'AcademicPress': [
        'AcademicPress',
        'Academic Press',
        'Academic Press is an imprint of Elsevier',
    ],
    'AddisonWesley': [
        'AddisonWesley',
        'Addison-Wesley Professional',
        'Addison-Wesley',
        'Addison Wesley',
        'addison wesley',
    ],
    'AtlantisPress': [
        'Atlantis Press',
        'AtlantisPress',
    ],
    'FeedBooks': [
        'FeedBooks',
        'This book is brought to you by Feedbooks',
        'http://www.feedbooks.com',
    ],
    'ProjectGutenberg': [
        'ProjectGutenberg',
        'Project Gutenberg',
        'www.gutenberg.net',
    ],
    'Apress': [
        'Apress',
        'apress',
        'www.apress.com',
    ],
    'BigNerdRanch': [
        'BigNerdRanch',
        'Big Nerd Ranch',
        'Big Nerd Ranch, Inc.',
        'www.bignerdranch.com',
    ],
    'CambridgeUP': [
        'CambridgeUP',
        'Cambridge University Press',
    ],
    'ChelseaHouse': [
        'Chelsea House',
        'ChelseaHouse',
    ],
    'CRCPress': [
        'CRCPress',
        'CRC Press',
        'www.crcpress.com',
    ],
    'CourseTechnology': [
        'Course Technology/Cengage Learning',
        'Cengage Learning',
        'CourseTechnology',
        'Course Technology',
        'Course Technology PTR',
        'Course Technology U.S.',
    ],
    'DennisPub': [
        'Dennis Pub.',
        'DennisPub',
    ],
    'Elsevier': [
        'Elsevier/Morgan Kaufmann',
        'Elsevier Science',
        'Elsevier',
    ],
    'IABooks': [
        'Indo American Books',
        'IA Books',
        'IABooks',
        'sales@iabooks.com',
        'www.iabooks.com',
    ],
    'ImperialCollegePress': [
        'ImperialCollegePress',
        'Imperial College Press',
    ],
    'JonesBartlett': [
        'JonesBartlett',
        'Jones and Bartlett Publishers',
        'Jones and Bartlett',
        'www.jbpub.com',
    ],
    'Manning': [
        'Manning Publications',
        'Manning',
    ],
    'McGrawHill': [
        'McGraw Hill Professional',
        'McGraw-Hill',
        'McGrawHill',
        'The McGraw-Hill Companies',
    ],
    'MicrosoftPress': [
        'Microsoft Press',
        'MicrosoftPress',
        'Microsoft Pr',
    ],
    'MITPress': [
        'MIT Press',
        'MITPress',
        'mitpress.mit.edu',
    ],
    'MorganKaufmann': [
        'Morgan Kaufmann Publishers',
        'Morgan Kaufmann',
        'MorganKaufmann',
    ],
    'NewAgeInt': [
        'NewAgeInt',
        'New Age International',
    ],
    'NoStarchPress': [
        'No Starch Press, Inc.',
        'No Starch Press Inc.',
        'No Starch Press',
        'NoStarchPress Inc.',
        'NoStarchPress',
        'www.nostarch.com',
    ],
    'OReilly':  [
        'OReilly',
        'oreilly',
        "O'Reilly Media"
        "O'Reilly"
        'O\u2019Reilly Media, Inc.'
        "O'Reilly & Associates"
        'Oreilly & Associates Inc',
        'Oreilly & Associates',
    ],
    'OxfordUP': [
        'OxfordUP',
        'Oxford University Press',
    ],
    'Packt': [
        'Packt',
        'Packt Publishing Limited',
        'Packt Publishing',
        'Packt Publ.',
        'Packt Pub.',
        'Published by Packt Publishing Ltd.',
        'www.packtpub.com',
    ],
    'PeachpitPress': [
        'PeachpitPress',
        'Peachpit Press',
        'peachpit.com',
    ],
    'Pearson': [
        'Pearson',
        'Pearson/PrenticeHall',
        'Pearson Education',
    ],
    'PragmaticBookshelf': [
        'PragmaticBookshelf',
        'The Pragmatic Bookshelf',
        'The Pragmatic Programmers, LLC.',
    ],
    'PrenticeHall': [
        'Prentice Hall',
        'PrenticeHall',
        'PRENTICE HALL',
    ],
    'Sams': [
        'Sams',
        'Sams Publishing',
        'samspublishing.com',
    ],
    'Springer': [
        'springer',
        'Springer Berlin',
        'Springer-Verlag New York Inc',
        'Springer-Verlag',
    ],
    'StanfordUP': [
        'StanfordUP',
        'Stanford University Press',
    ],
    'Syngress': [
        'Syngress',
        'syngress',
        'Syngress Media Inc',
        'Syngress Pub.',
        'www.syngress.com',
    ],
    'TaylorFrancis': [
        'TaylorFrancis',
        'Taylor and Francis',
    ],
    'Wiley': [
        'John Wiley & Sons, Inc.',
        'John Wiley & Sons Inc',
        'John Wiley & Sons',
        'John Wiley',
        'J. Wiley',
        'Wiley Pub., Inc.',
        'Wiley Pub.',
        'wiley & Sons',
        'wiley',
    ],
    'Wordware': [
        'Wordware',
        'Wordware Pub',
        'Wordware Pub.',
        'Wordware Publ',
        'Wordware Publishing',
    ],
    'WorldScientific': [
        'WorldSci',
        'WorldScientific',
        'World Scientific',
    ],
    'Wrox': [
        'Wrox',
        'Wrox/John Wiley & Sons',
        'www.wrox.com',
    ]
}


class TestStringValueCanonicalizer(TestCase):
    def test_filepath_config_is_expected_absolute_path(self):
        c = StringValueCanonicalizer(b'canonical_publisher.yaml')
        actual = c.filepath_config

        self.assertIsInstance(actual, bytes)
        self.assertTrue(actual.endswith(b'canonical_publisher.yaml'))
        self.assertTrue(uu.is_abspath(actual))

    def test_returns_given_as_is_when_used_as_callable(self):
        c = StringValueCanonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning')
        self.assertEqual('Manning', actual)

    def test_returns_expected_when_used_as_callable(self):
        c = StringValueCanonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning Publications')
        self.assertEqual('Manning', actual)


class TestCanonicalizePublisher(TestCase):
    def test_canonicalize_publisher(self):
        for canonical, equivalent_values in PUBLISHER_CANONICAL_EQUIVALENTS.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given=equivalent_value):
                    actual = _canonicalize_publisher(equivalent_value)
                    self.assertEqual(canonical, actual)

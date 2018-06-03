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

import re
from unittest import TestCase

import unit.utils as uu
from core.metadata.canonicalize import build_string_value_canonicalizer
from core.metadata.canonicalize import CanonicalizerConfigParser
from core.metadata.canonicalize import canonicalize_publisher
from core.metadata.canonicalize import StringValueCanonicalizer


def _canonicalize_publisher(given):
    return canonicalize_publisher(given)


def _build_string_value_canonicalizer(*args, **kwargs):
    return build_string_value_canonicalizer(*args, **kwargs)


def _get_canonicalizer_config_parser(*args, **kwargs):
    return CanonicalizerConfigParser(*args, **kwargs)


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
    'AthenaScientific': [
        'AthenaScientific',
        'Athena Scientific',
    ],
    'AtlantisPress': [
        'Atlantis Press',
        'AtlantisPress',
    ],
    'ArtechHouse': [
        'ArtechHouse',
        'Artech House',
    ],
    'Barrons': [
        "Barron's Educational Series Inc",
        "Barron's Educational Series Inc.",
        "Barron's Educational Series",
        "Barron's Educational Series, Inc",
        "Barron's Educational Series, Inc.",
        "Barron\u2019s Educational Series Inc",
        "Barron\u2019s Educational Series Inc.",
        "Barron\u2019s Educational Series",
        "Barron\u2019s Educational Series, Inc",
        "Barron\u2019s Educational Series, Inc.",
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
    'AZElitePub': [
        'AZ Elite',
        'AZ Elite Pub',
        'AZ Elite Pub.',
        'AZ Elite Publ',
        'AZ Elite Publ.',
        'AZ Elite Publishing',
    ],
    'BigNerdRanch': [
        'Big Nerd Ranch Inc.',
        'Big Nerd Ranch Incorporated',
        'Big Nerd Ranch',
        'Big Nerd Ranch, Inc.',
        'Big Nerd Ranch, Incorporated',
        'BigNerdRanch',
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
        'Chapman & Hall/CRC',
        'Chapman and Hall/CRC',
        'Chapman & Hall/CRC Press',
        'Chapman and Hall/CRCPress',
        'CRCPress',
        'CRC Press',
        'www.crcpress.com',
    ],
    'Cengage': [
        'Brooks/Cole Cengage Learning',
        'Brooks/Cole Cengage',
        'Brooks/Cole, Cengage Learning',
        'Cengage Learning',
        'Cengage',
        'Course Technology PTR',
        'Course Technology U.S.',
        'Course Technology',
        'Course Technology/Cengage Learning',
        'CourseTechnology',
    ],
    'CyberPunkUni': [
        'Cyberpunk University',
        'CyberPunkUni',
        'University, Cyberpunk',
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
    'ExelixisMedia': [
        'Exelixis Media P.C.',
    ],
    'FranklinBeedle': [
        'Franklin, Beedle & Associates',
        'Franklin, Beedle and Associates',
        'Franklin, Beedle, and Associates',
        'Franklin Beedle & Associates',
        'Franklin Beedle and Associates',
        'Franklin Beedle, and Associates',
        'Franklin, Beedle & Associates Inc.',
        'Franklin, Beedle and Associates Inc.',
        'Franklin, Beedle, and Associates Inc.',
        'Franklin, Beedle & Associates Incorporated',
        'Franklin, Beedle and Associates Incorporated',
        'Franklin, Beedle, and Associates Incorporated',
    ],
    'IABooks': [
        'IA Books',
        'IABooks',
        'Indo American Books',
        'sales@iabooks.com',
        'www.iabooks.com',
    ],
    'IGIGlobal': [
        'IGIGlobal',
        'IGI Global',
    ],
    'ImperialCollegePress': [
        'ImperialCollegePress',
        'Imperial College Press',
    ],
    'ITAcademy': [
        'ITAcademy',
        'IT Academy',
    ],
    'JohnsHopkinsUP': [
        'Johns Hopkins University Press Ltd',
        'Johns Hopkins University Press Ltd. London',
        'Johns Hopkins University Press Ltd.',
        'Johns Hopkins University Press Ltd., London',
        'Johns Hopkins University Press',
        'The Johns Hopkins University Press Ltd',
        'The Johns Hopkins University Press Ltd. London',
        'The Johns Hopkins University Press Ltd.',
        'The Johns Hopkins University Press Ltd., London',
        'The Johns Hopkins University Press',
    ],
    'JonesBartlett': [
        'Jones and Bartlett Publishers',
        'Jones and Bartlett',
        'JonesBartlett',
        'www.jbpub.com',
    ],
    'LCFPub': [
        'LCF Publishing',
        'LCFPub',
        'LCFPublishing',
        'Learn Coding Fast',
        'Publishing LCF',
        'Publishing, LCF',
    ],
    'Leanpub': [
        'Leanpub',
        'leanpub',
    ],
    'LuLu': [
        '[Lulu Press], lulu.com',
        'Lulu Press',
    ],
    'Manning': [
        'Manning Publications',
        'Manning',
    ],
    'McGrawHill': [
        'McGraw Hill Irwin',
        'McGraw Hill Professional',
        'McGraw Hill',
        'McGraw-Hill Education TAB',
        'McGraw-Hill Irwin',
        'McGraw-Hill',
        'McGrawHill Irwin',
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
        'M I T Press',
    ],
    'MorganKaufmann': [
        'Morgan Kaufmann Publishers',
        'Morgan Kaufmann',
        'MorganKaufmann',
    ],
    'MorganClaypool': [
        'Morgan & Claypool Publishers',
        'Morgan and Claypool Publishers'
    ],
    'NewAgeInt': [
        'NewAgeInt',
        'New Age International',
    ],
    'NoStarchPress': [
        'No Starch Press Inc.',
        'No Starch Press Incorporated',
        'No Starch Press',
        'No Starch Press, Inc.',
        'No Starch Press, Incorporated',
        'No Starch',
        'NoStarchPress Inc.',
        'NoStarchPress Incorporated',
        'NoStarchPress',
        'NoStarchPress, Inc.',
        'NoStarchPress, Incorporated',
        'www.nostarch.com',
    ],
    'OReilly':  [
        "O'Reilly & Associates",
        "O'Reilly and Associates",
        "O'Reilly Media Inc",
        "O'Reilly Media Inc.",
        "O'Reilly Media",
        "O'Reilly Media, Inc",
        "O'Reilly Media, Inc.",
        "O'Reilly",
        "OReilly Media Inc",
        "OReilly Media Inc.",
        "OReilly Media, Inc",
        "OReilly Media, Inc.",
        'O\u2019Reilly Media Inc',
        'O\u2019Reilly Media Inc.',
        'O\u2019Reilly Media Incorporated',
        'O\u2019Reilly Media, Inc',
        'O\u2019Reilly Media, Inc.',
        'O\u2019Reilly Media, Incorporated',
        'Oreilly & Associates Inc',
        'Oreilly & Associates Incorporated',
        'Oreilly & Associates',
        'Oreilly & Associates, Inc',
        'Oreilly & Associates, Incorporated',
        'Oreilly and Associates Inc',
        'Oreilly and Associates Inc.',
        'Oreilly and Associates Incorporated',
        'Oreilly and Associates',
        'Oreilly and Associates, Inc',
        'Oreilly and Associates, Inc.',
        'Oreilly and Associates, Incorporated',
        'OReilly',
        'oreilly',
    ],
    'OxfordUP': [
        'OxfordUP',
        'Oxford University Press',
    ],
    'Packt': [
        'Packt Pub. Limited',
        'Packt Pub. Ltd',
        'Packt Pub. Ltd.',
        'Packt Pub.',
        'Packt Publ. Limited',
        'Packt Publ. Ltd',
        'Packt Publ. Ltd.',
        'Packt Publ.',
        'Packt Publishing Limited',
        'Packt Publishing Ltd',
        'Packt Publishing Ltd.',
        'Packt Publishing',
        'Packt',
        'Published by Packt Publishing Ltd.',
        'www.packtpub.com',
    ],
    'PeachpitPress': [
        'PeachpitPress',
        'Peachpit Press',
        'peachpit.com',
    ],
    'Pearson': [
        'Pearson Education Inc',
        'Pearson Education Inc.',
        'Pearson Education Incorporated',
        'Pearson Education',
        'Pearson Education, Inc',
        'Pearson Education, Inc.',
        'Pearson Education, Incorporated',
        'Pearson',
        'Pearson/AddisonWesley',
        'Pearson/PrenticeHall',
    ],
    'PragmaticBookshelf': [
        'Pragmatic Bookshelf',
        'PragmaticBookshelf',
        'The Pragmatic Bookshelf',
        'The Pragmatic Programmers LLC',
        'The Pragmatic Programmers',
        'The Pragmatic Programmers, LLC.',
    ],
    'PrenticeHall': [
        'Prentice Hall',
        'PrenticeHall',
        'PRENTICE HALL',
        'Prentice Hall PTR',
    ],
    'PublishOrPerish': [
        'Publish or Perish Inc',
        'Publish or Perish inc',
        'Publish or Perish Inc.',
        'Publish or Perish inc.',
        'Publish or Perish Incorporated',
        'Publish or Perish',
        'Publish or Perish, Inc.',
        'Publish or Perish, inc.',
        'Publish or Perish, Incorporated',
    ],
    'Routledge': [
        'Routledge Publishing',
        'Routledge Taylor & Francis Group',
        'Routledge Taylor and Francis Group',
        'Routledge',
    ],
    'Sams': [
        'Sams',
        'Sams Publishing',
        'samspublishing.com',
    ],
    'Springer': [
        'Springer Berlin',
        'SPRINGER VERLAG (NY/NJ)',
        'Springer Verlag New York Inc',
        'Springer Verlag New York Inc.',
        'Springer Verlag New York Incorporated',
        'Springer Verlag',
        'springer',
        'Springer-Verlag New York Inc',
        'Springer-Verlag New York Inc.',
        'Springer-Verlag New York Incorporated',
        'Springer-Verlag',
    ],
    'StanfordUP': [
        'StanfordUP',
        'Stanford University Press',
    ],
    'Syngress': [
        'Syngress Media Inc',
        'Syngress Media Inc.',
        'Syngress Media Incorporated',
        'Syngress Pub',
        'Syngress Pub.',
        'Syngress Publishing',
        'Syngress',
        'syngress',
        'www.syngress.com',
    ],
    'TaylorFrancis': [
        'Taylor & Francis',
        'Taylor and Francis',
        'TaylorFrancis',
    ],
    'WellesleyCambridge': [
        'Wellesley Cambridge Press',
        'Wellesley Cambridge',
        'Wellesley-Cambridge Press',
        'Wellesley-Cambridge',
        'WellesleyCambridgePress',
    ],
    'Westview': [
        'Westview',
    ],
    'Wiley': [
        'J. Wiley',
        'John Wiley & Sons Inc',
        'John Wiley & Sons Incorporated',
        'John Wiley & Sons',
        'John Wiley & Sons, Inc.',
        'John Wiley & Sons, Incorporated',
        'John Wiley and Sons Inc',
        'John Wiley and Sons Incorporated',
        'John Wiley and Sons',
        'John Wiley and Sons, Inc.',
        'John Wiley and Sons, Incorporated',
        'John Wiley',
        'wiley & Sons',
        'wiley and Sons',
        'Wiley Pub',
        'Wiley Pub.',
        'Wiley Pub., Inc.',
        'Wiley Pub., Incorporated',
        'wiley',
        'Wiley-Interscience',
    ],
    'Wordware': [
        'Wordware Pub',
        'Wordware Pub.',
        'Wordware Publ',
        'Wordware Publishing',
        'Wordware',
    ],
    'WorldScientific': [
        'WorldSci',
        'WorldScientific',
        'World Scientific',
    ],
    'Wrox': [
        'Wrox',
        'Wrox/John Wiley & Sons',
        # 'Wrox/John Wiley and Sons',
        # 'Wrox/Wiley & Sons',
        # 'Wrox/Wiley and Sons',
        'www.wrox.com',
    ]
}


class TestCanonicalizerConfigParser(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.SECTION_MATCH_ANY_LITERAL = CanonicalizerConfigParser.CONFIG_SECTION_MATCH_ANY_LITERAL
        cls.SECTION_MATCH_ANY_REGEX = CanonicalizerConfigParser.CONFIG_SECTION_MATCH_ANY_REGEX

    def _get_parser_from_empty_config(self):
        empty_config = dict()
        return _get_canonicalizer_config_parser(empty_config)

    def _get_parser_from_config(self, config):
        return _get_canonicalizer_config_parser(config)

    def _compile_regex(self, pattern):
        # NOTE: Compilation flags must match those used in the implementation.
        return re.compile(pattern, re.IGNORECASE)

    def test_filepath_config_is_expected_absolute_path(self):
        empty_config = dict()
        parser = _get_canonicalizer_config_parser(empty_config, b'/tmp/canonical_publisher.yaml')
        actual = parser.str_lookup_dict_filepath
        self.assertIsInstance(actual, str,
                              '*not bytestring* path is stored for logging only')
        self.assertTrue(actual.endswith('canonical_publisher.yaml'))
        self.assertTrue(uu.is_abspath(actual))

    def test_can_be_instantiated_with_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertIsNotNone(parser)

    def test_parsed_literal_lookup_is_empty_when_given_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_parsed_literal_lookup_is_empty_when_given_only_empty_strings(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_parsed_literal_lookup_is_empty_when_given_empty_literals(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': set([
                'Foo',
                'foo pub'
             ])
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': set([
                'Foo',
                'foo pub'
             ]),
            'BarPub': set([
                'Bar Publishers Inc.',
                'bar pub.'
             ])
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_only_empty_strings(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_empty_regex(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_returns_expected_parsed_regex_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = {
            'FooPub': set([
                self._compile_regex('Foo'),
                self._compile_regex('foo pub')
             ])
        }
        self.assertEqual(expect_parsed_regex_lookup, parser.parsed_regex_lookup)

    def test_returns_expected_parsed_regex_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = {
            'FooPub': set([
                self._compile_regex('Foo'),
                self._compile_regex('foo pub')
             ]),
            'BarPub': set([
                self._compile_regex('Bar Publishers Inc.'),
                self._compile_regex('bar pub.')
             ])
        }
        self.assertEqual(expect_parsed_regex_lookup, parser.parsed_regex_lookup)


class TestBuildStringValueCanonicalizer(TestCase):
    def test_returns_given_as_is_when_used_as_callable(self):
        c = _build_string_value_canonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning')
        self.assertEqual('Manning', actual)

    def test_returns_expected_when_used_as_callable(self):
        c = _build_string_value_canonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning Publications')
        self.assertEqual('Manning', actual)


class TestCanonicalizePublisher(TestCase):
    def test_canonicalize_publisher(self):
        for canonical, equivalent_values in PUBLISHER_CANONICAL_EQUIVALENTS.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given_expected=(equivalent_value, canonical)):
                    actual = _canonicalize_publisher(equivalent_value)
                    self.assertEqual(canonical, actual)


class TestStringValueCanonicalizer(TestCase):
    def _compile_regex(self, pattern):
        # NOTE: Compilation flags must match those used in the implementation.
        return re.compile(pattern, re.IGNORECASE)

    def test_returns_values_as_is_when_given_empty_lookup_data(self):
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=dict())

        for given_and_expected in [
            '',
            'foo',
            'foo bar'
        ]:
            with self.subTest(given_and_expected=given_and_expected):
                actual = c(given_and_expected)
                self.assertEqual(given_and_expected, actual)

    def test_replaces_one_value_matching_one_regex_pattern(self):
        regex_lookup_dict = {
            'BAZ': [
                self._compile_regex('.*foo')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given in [
            'foo',
            'foo foo',
            'fooo',
            'fooo foo',
            'foo fooo',
            'foo bar',
            'fooo bar',
            'bar foo',
            'bar foo',
        ]:
            with self.subTest():
                actual = c(given)
                self.assertEqual('BAZ', actual)

    def test_replaces_two_values_matching_one_regex_pattern_each(self):
        regex_lookup_dict = {
            'BAZ': [
                self._compile_regex('foo')
            ],
            'MEOW': [
                self._compile_regex('w')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('BAZ',     'BAZ'),
            ('baz',     'BAZ'),
            ('foo',     'BAZ'),
            ('foo foo', 'BAZ'),

            ('MEOW', 'MEOW'),
            ('meow', 'MEOW'),
            ('w',    'MEOW'),
            ('ww',   'MEOW'),

            # Patterns for both 'BAZ' and 'MEOW' match.
            # TODO: [incomplete] Result depends on order in 'value_lookup_dict'.. ?
            ('foow', 'BAZ'),
            ('foo w', 'BAZ'),
            ('w foo', 'BAZ'),
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)

        # Expect these to not match and be passed through as-is.
        for given_and_expected in [
            'BAZ BAZ',
            'baz baz',
        ]:
            with self.subTest():
                actual = c(given_and_expected)
                self.assertEqual(given_and_expected, given_and_expected)

    def test_uses_value_with_longest_match_in_case_of_conflicts(self):
        regex_lookup_dict = {
            'FOO': [
                self._compile_regex('F+')
            ],
            'BAR': [
                self._compile_regex('B+')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('F',     'FOO'),
            ('FF',    'FOO'),
            ('FFB',   'FOO'),
            ('BFF',   'FOO'),
            # ('FFBB',  'FOO'),  # TODO: Handle tied match lengths?
            ('B',     'BAR'),
            ('BB',    'BAR'),
            ('BBF',   'BAR'),
            ('FBB',   'BAR'),
            # ('BBFF',  'BAR'),  # TODO: Handle tied match lengths?
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)

    def test_uses_value_with_longest_match_in_case_of_conflicts_multiple_patterns(self):
        regex_lookup_dict = {
            'FOO': [
                self._compile_regex('f+'),
                self._compile_regex('x+')
            ],
            'BAR': [
                self._compile_regex('b+'),
                self._compile_regex('y+')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('f',     'FOO'),
            ('ff',    'FOO'),
            ('x',     'FOO'),
            ('xx',    'FOO'),
            ('fx',    'FOO'),
            ('xf',    'FOO'),
            ('xxff',  'FOO'),
            ('ffxx',  'FOO'),

            ('b',     'BAR'),
            ('bb',    'BAR'),
            ('y',     'BAR'),
            ('yy',    'BAR'),
            ('by',    'BAR'),
            ('yb',    'BAR'),
            ('yybb',  'BAR'),
            ('bbyy',  'BAR'),

            ('ffb',   'FOO'),
            ('bff',   'FOO'),
            ('ffy',   'FOO'),
            ('yff',   'FOO'),

            ('fbb',   'BAR'),
            ('bbf',   'BAR'),
            ('bbx',   'BAR'),
            ('xbb',   'BAR'),

            # ('ffBB',  'FOO'),  # TODO: Handle tied match lengths?
            # ('bbFF',  'BAR'),  # TODO: Handle tied match lengths?

            ('ffff bb',  'FOO'),
            ('fxfx bb',  'FOO'),
            ('fxxx bb',  'FOO'),
            ('xxxx bb',  'FOO'),

            ('bbbb ff',  'BAR'),
            ('byyy ff',  'BAR'),
            ('yyyy ff',  'BAR'),

            ('bb ffff',  'FOO'),
            ('ff ff bb', 'FOO'),
            ('bb ff ff', 'FOO'),

            ('ff bbb',  'BAR'),
            ('ff bbbb', 'BAR'),
            ('bbb ff',  'BAR'),
            ('bbbb ff', 'BAR'),

            ('ffff _ bb',   'FOO'),
            ('ffff _ bb _', 'FOO'),
            ('bb _ ffff',   'FOO'),
            ('ff _ ff bb',  'FOO'),
            ('bb _ ffff',   'FOO'),
            ('_ bb _ ffff', 'FOO'),
            ('_ fff _ bb',  'FOO'),
            ('_ bb _ ffff', 'FOO'),
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)

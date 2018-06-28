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
from core.metadata.canonicalize import canonicalize_creatortool
from core.metadata.canonicalize import canonicalize_language
from core.metadata.canonicalize import canonicalize_publisher
from core.metadata.canonicalize import StringValueCanonicalizer


def _canonicalize_publisher(given):
    return canonicalize_publisher(given)


def _canonicalize_language(given):
    return canonicalize_language(given)


def _canonicalize_creatortool(given):
    return canonicalize_creatortool(given)


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
        'Addison Wesley Professional',
        'Addison Wesley Profressional',
        'Addison Wesley Pub Co',
        'Addison Wesley Pub Co.',
        'Addison Wesley Pub. Co',
        'Addison Wesley Pub. Co.',
        'Addison Wesley Publ Co',
        'Addison Wesley Publ Co.',
        'Addison Wesley Publ. Co',
        'Addison Wesley Publ. Co.',
        'Addison Wesley Publishing Co',
        'Addison Wesley Publishing Co.',
        'Addison Wesley Publishing Company',
        'addison wesley',
        'Addison Wesley',
        'Addison-Wesley Professional',
        'Addison-Wesley Profressional',
        'Addison-Wesley Pub Co',
        'Addison-Wesley Pub Co.',
        'Addison-Wesley Pub. Co',
        'Addison-Wesley Pub. Co.',
        'Addison-Wesley Publ Co',
        'Addison-Wesley Publ Co.',
        'Addison-Wesley Publ. Co',
        'Addison-Wesley Publ. Co.',
        'Addison-Wesley Publishing Co',
        'Addison-Wesley Publishing Co.',
        'Addison-Wesley Publishing Company',
        'Addison-Wesley',
    ],
    'AKPeters': [
        'AKPeters',
        'AK Peters',
        'A K Peters',
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
    'BackupBrain': [
        'backupbrain',
        'backupbrain pub',
        'backupbrain pub.',
        'backupbrain publ',
        'backupbrain publ.',
        'backupbrain publishing',
        'backup brain',
        'backup brain pub',
        'backup brain pub.',
        'backup brain publ',
        'backup brain publ.',
        'backup brain publishing',
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
    'BleedingEdgePress': [
        'BleedingEdgePress',
        'Bleeding Edge Press',
    ],
    'BonsaiReads': [
        'BonsaiReads',
        'Bonsai Reads',
    ],
    'BookBoon': [
        'BookBoon',
        'Bookboon',
        'Bookboon.com',
        'Bookboon.com Ltd',
        'Bookboon.com Ltd.',
        'Bookboon.com Limited',
    ],
    'ClydeBank': [
        'ClydeBank',
        'ClydeBank Media',
        'ClydeBank Media LLC',
        'ClydeBank Technology',
        'www.clydebankmedia.com',
    ],
    'CodeWellAcademy': [
        'CodeWellAcademy',
        'Code Well Academy',
    ],
    'CreateSpace': [
        'Createspace',
        'CreateSpace',
        'Createspace Independent Publishing Platform',
    ],
    'FeedBooks': [
        'FeedBooks',
        'This book is brought to you by Feedbooks',
        'http://www.feedbooks.com',
        'www.feedbooks.com',
    ],
    'GrinPub': [
        'GrinPub',
        'GRIN Publishing',
        'GRIN Verlag',
        'GRIN Verlag Open Publishing GmbH',
        'GRIN Verlag Open Publishing',
        'GRIN Verlag, Open Publishing GmbH',
        'GRIN Verlag, Open Publishing',
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
    'HeatonResearch': [
        'HeatonResearch',
        'Heaton Research',
        'Heaton Research Inc',
        'Heaton Research Inc.',
        'Heaton Research Incorporated.',
        'Heaton Research, Inc',
        'Heaton Research, Inc.',
        'Heaton Research, Incorporated.',
    ],
    'HodderStoughton': [
        'Hodder & Stoughton',
        'Hodder and Stoughton',
        'HodderStoughton',
    ],
    'HoughtonMifflin': [
        'HoughtonMifflin',
        'Houghton Mifflin',
    ],
    'HunanCartographic': [
        'Hunan Cartographic Pub',
        'Hunan Cartographic Pub.',
        'Hunan Cartographic Publ',
        'Hunan Cartographic Publ.',
        'Hunan Cartographic Publishing',
        'Hunan Cartographic Publishing House',
    ],
    'IABooks': [
        'IA Books',
        'IABooks',
        'Indo American Books',
        'sales@iabooks.com',
        'www.iabooks.com',
    ],
    'IdeaGroup': [
        'IdeaGroup',
        'Idea Group',
        'Idea group',
    ],
    'IGIGlobal': [
        'IGIGlobal',
        'IGI Global',
    ],
    'ImperialCollegePress': [
        'ImperialCollegePress',
        'Imperial College Press',
    ],
    'IBMITSO': [
        'IBMITSO',
        'IBM International Technical Support Organization',
        'IBM Red Books',
        'IBM Redbooks',
        'International Technical Support Organization',
    ],
    'ITAcademy': [
        'ITAcademy',
        'IT Academy',
    ],
    'JohnsHopkinsUP': [
        'JohnsHopkinsUP',
        'Johns Hopkins University Press Ltd',
        'Johns Hopkins University Press Ltd. London',
        'Johns Hopkins University Press Ltd.',
        'Johns Hopkins University Press Ltd., London',
        'Johns Hopkins University Press Limited, London',
        'Johns Hopkins University Press Limited London',
        'Johns Hopkins University Press',
        'The Johns Hopkins University Press Ltd',
        'The Johns Hopkins University Press Limited',
        'The Johns Hopkins University Press Ltd. London',
        'The Johns Hopkins University Press Limited London',
        'The Johns Hopkins University Press Ltd.',
        'The Johns Hopkins University Press Ltd., London',
        'The Johns Hopkins University Press Limited, London',
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
    'LondonPub': [
        'LondonPub',
        'London Publishing Partnership',
    ],
    'LuLu': [
        'Lulu',
        '[Lulu Press], lulu.com',
        'Lulu Press',
        'lulu.com',
        'Lulu.com',
    ],
    'MakerMedia': [
        'MakerMedia',
        'Maker Media Inc',
        'Maker Media Inc.',
        'Maker Media Incorporated',
        'Maker Media, Inc',
        'Maker Media, Inc.',
        'Maker Media, Incorporated',
    ],
    'Manning': [
        'Manning',
        'Manning Pub Company',
        'Manning Pub',
        'Manning Pub. Company',
        'Manning Pub.',
        'Manning Publ Company',
        'Manning Publ',
        'Manning Publ. Company',
        'Manning Publ.',
        'Manning Publications Company',
        'Manning Publications',
    ],
    'McGrawHill': [
        'McGraw',
        'McGrawHill',
        'McGraw Hill',
        'McGraw Hill Education TAB',
        'McGraw Hill Education',
        'McGraw Hill Irwin',
        'McGraw Hill Osborne',
        'McGraw Hill Professional',
        'McGraw Hill/Irwin',
        'McGraw Hill/Osborne',
        'McGraw-Hill Education TAB',
        'McGraw-Hill Education',
        'McGraw-Hill Irwin',
        'McGraw-Hill Osborne',
        'McGraw-Hill',
        'Mcgraw-Hill',
        'McGraw-Hill/Irwin',
        'McGraw-Hill/Osborne',
        'McGrawHill Education TAB',
        'McGrawHill Education',
        'McGrawHill Irwin',
        'McGrawHill Osborne',
        'McGrawHill/Irwin',
        'McGrawHill/Osborne',
        'The McGraw Hill Companies',
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
    'Murachs': [
        'Murachs',
    ],
    'NewAgeInt': [
        'NewAgeInt',
        'New Age International',
    ],
    'NewRiders': [
        'NewRiders',
        'New Riders',
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
    'OhmBooks': [
        'OhmBooks',
        'Ohm Books',
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
    'PeepPress': [
        'PeepPress',
        'Peep Press',
        'Peep! Press',
    ],
    'PenguinRandomHouse': [
        'Penguin Random House',
        'Penguin Random House India',
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
    'PrincetonUP': [
        'PrincetonUP',
        'Princeton University Press',
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
    'RecursiveBooks': [
        'RecursiveBooks',
        'Recursive Books',
    ],
    'Sams': [
        'Sams',
        'Sams Publishing',
        'samspublishing.com',
    ],
    'SimpleProgrammer': [
        'SimpleProgrammer',
        'Simple Programmer',
    ],
    'SitePoint': [
        'SitePoint',
        'SitePoint Ltd',
        'SitePoint Ltd.',
        'SitePoint Pty Ltd',
        'SitePoint Pty. Ltd.',
        'SitePoint Proprietary Ltd.',
        'SitePoint Proprietary Ltd',
        'SitePoint Proprietary Limited',
    ],
    'SkriptKuhnel': [
        'SkriptKuhnel',
        'Skript-Verl. Kühnel',
        'Skript-Verl Kühnel',
        'Skript-Verlag Kühnel',
        'Skript-Verl. Kuhnel',
        'Skript-Verl Kuhnel',
        'Skript-Verlag Kuhnel',
    ],
    'Springer': [
        'Springer',
        'Imprint Springer',
        'Imprint: Springer',
        'Springer Berlin',
        'Springer London',
        'Springer New York',
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
        'Syngress Media',
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
    'TuttlePub': [
        'TuttlePublishing',
        'Tuttle',
        'Tuttle Pub',
        'Tuttle Pub.',
        'Tuttle Publ',
        'Tuttle Publ.',
        'Tuttle Publishing',
    ],
    'UnitedComputerGeeks': [
        'UnitedComputerGeeks',
        'United Computer Geeks',
    ],
    'WalterdeGruyter': [
        'WalterdeGruyter',
        'Walter de Gruyter',
        'Walter de Gruyter GmbH & Co KG',
        'Walter de Gruyter GmbH and Co KG',
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
        'Wiley',
        'wiley',
        'Wiley-Blackwell',
        'Wiley/Blackwell',
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
        'Wiley Technology Pub',
        'Wiley Technology Pub.',
        'Wiley Technology Publishing',
        'Wiley Technology',
        'Wiley-Interscience',
    ],
    'Wordware': [
        'Wordware Pub',
        'Wordware Pub.',
        'Wordware Publ',
        'Wordware Publishing',
        'Wordware',
    ],
    'NewEnglishReview': [
        'New English Review Press',
        'World Encounter Institute',
        'World Encounter Institute/New English Review Press',
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
        'Wrox Pr Inc',
        'Wrox Pr. Inc',
        'Wrox Pr. Inc.',
        'Wrox Press Inc',
        'Wrox Press Inc.',
        'Wrox Press',
    ]
}

LANGUAGE_CANONICAL_EQUIVALENTS = {
    'ENGLISH': [
        'EN',
        'en',
        'ENG',
        'eng',
        'ENGLISH',
        'english',
    ],
    'SWEDISH': [
        'SV',
        'sv',
        'SWE',
        'swe',
        'SWEDISH',
        'swedish',
        'svenska',
        'SVENSKA',
    ],
}

CREATORTOOL_CANONICAL_EQUIVALENTS = {
    'Adobe Acrobat': [
        'Acrobat',
        'Adobe Acrobat',
        'Acrobat 10.1.10',
        'Acrobat 11.0.0',
        'Acrobat 11.0.10',
        'Acrobat 11.0.12',
        'Acrobat 11.0.23',
        'Acrobat 4.0 Capture Plug-in for Windows',
        'Acrobat 4.0 Import Plug-in for Macintosh',
        'Acrobat 4.0 Import Plug-in for Windows',
        'Acrobat 4.0 Scan Plug-in for Windows',
        'Acrobat 4.05 Import Plug-in for Windows',
        'Acrobat 5.0 Image Conversion Plug-in for Windows',
        'Acrobat 5.0 Paper Capture Plug-in for Windows',
        'Acrobat 9.0.0',
        'Acrobat 9.3.0',
        'Acrobat pictwpstops filter 1.0',
        'Acrobat pictwpstops filter 1.0(Infix Pro)',
        'Acrobat pictwpstops filter 1.0(Infix)',
        'Acrobat Pro 15.17.20053',
        'Acrobat Pro 15.20.20042',
        'Acrobat Pro 15.23.20056',
        'Acrobat Pro 15.9.20077',
        'Acrobat Pro DC 17.12.20098',
        'Acrobat Pro DC 17.9.20058',
        'Acrobat Pro DC 18.11.20038',
        'Acrobat Pro DC 18.9.20050',
        'Acrobat: pictwpstops filter 1.(Infix Pro(Infix Pro(Infix Pro(Infix Pro)',
        'Acrobat: pictwpstops filter 1.0',
        'Acrobat: pictwpstops filter 1.0(Infix Pro)',
        'Acrobat: pictwpstops filter 1.0(Infix)',
        'Adobe Acrobat 10.1.1',
        'Adobe Acrobat 10.1.8',
        'Adobe Acrobat 11.0.1',
        'Adobe Acrobat 11.0.13',
        'Adobe Acrobat 11.0.14',
        'Adobe Acrobat 11.0.20',
        'Adobe Acrobat 11.0.9',
        'Adobe Acrobat 15.9',
        'Adobe Acrobat 6.0',
        'Adobe Acrobat 6.01',
        'Adobe Acrobat 7.0',
        'Adobe Acrobat 7.05',
        'Adobe Acrobat 7.08',
        'Adobe Acrobat 7.1',
        'Adobe Acrobat 8.0 Combine Files',
        'Adobe Acrobat 8.0',
        'Adobe Acrobat 8.1 Combine Files',
        'Adobe Acrobat 8.1',
        'Adobe Acrobat 8.1.2',
        'Adobe Acrobat 8.12',
        'Adobe Acrobat 8.14',
        'Adobe Acrobat 8.2 Combine Files',
        'Adobe Acrobat 8.3 Combine Files',
        'Adobe Acrobat 9.0',
        'Adobe Acrobat 9.0.0',
        'Adobe Acrobat 9.1.2',
        'Adobe Acrobat 9.3',
        'Adobe Acrobat 9.3.4',
        'Adobe Acrobat 9.4.2',
        'Adobe Acrobat 9.4.6',
        'Adobe Acrobat Pro 10.0.0',
        'Adobe Acrobat Pro 10.0.0(Infix Pro)',
        'Adobe Acrobat Pro 10.0.2',
        'Adobe Acrobat Pro 10.0.3',
        'Adobe Acrobat Pro 10.1.0',
        'Adobe Acrobat Pro 10.1.1',
        'Adobe Acrobat Pro 10.1.11',
        'Adobe Acrobat Pro 10.1.16',
        'Adobe Acrobat Pro 10.1.2',
        'Adobe Acrobat Pro 10.1.8',
        'Adobe Acrobat Pro 11.0.0',
        'Adobe Acrobat Pro 11.0.15',
        'Adobe Acrobat Pro 11.0.3',
        'Adobe Acrobat Pro 11.0.7',
        'Adobe Acrobat Pro 9.0.0',
        'Adobe Acrobat Pro 9.1.0',
        'Adobe Acrobat Pro 9.3.3',
        'Adobe Acrobat Pro 9.3.4',
        'Adobe Acrobat Pro 9.4.5',
        'Adobe Acrobat Pro 9.4.6',
        'Adobe Acrobat Pro 9.4.6(Infix Pro)',
        'Adobe Acrobat Pro 9.5.1',
        'Adobe Acrobat Pro 9.5.2',
        'Adobe Acrobat Pro 9.5.5',
        'Adobe Acrobat Pro Extended 9.0.0',
        'Adobe Acrobat Pro Extended 9.2.0',
        'Adobe Acrobat Pro Extended 9.3.2',
        'Adobe Acrobat Pro Extended 9.5.5',
        'Quite Imposing',
        'Quite Imposing 1.5d (EN)',
        'Quite Imposing 1.5d (EN)(Infix Pro)',
        'Quite Imposing 2.9b',
    ],
    'Adobe Acrobat Distiller': [
        'Acrobat Distiller',
        'Acrobat Distiller 10.0.0 (Windows)',
        'Acrobat Distiller 10.0.0',
        'ADOBEPS4.DRV Version 4.10',
        'ADOBEPS4.DRV',
        'AdobePS5.dll Version 5.2',
        'AdobePS5.dll Version 5.2.2',
        'AdobePS5.dll',
    ],
    'Adobe Acrobat PDFMaker': [
        'Adobe Acrobat PDFMaker',
    ],
    'Adobe FrameMaker': [
        'Adobe FrameMaker',
        'FrameMaker 2017.0.2',
        'FrameMaker 5.5.3L15a',
        'FrameMaker 5.5.6.',
        'FrameMaker 5.5.6p145',
        'FrameMaker 5.5P4f',
        'FrameMaker 6.0',
        'FrameMaker 6.0: AdobePS 8.6 (219)',
        'FrameMaker 6.0: AdobePS 8.8.0 (301)',
        'FrameMaker 7.0',
        'FrameMaker 7.1',
        'FrameMaker 7.2',
        'FrameMaker 8.0',
        'FrameMaker 8.0(Foxit Advanced PDF Editor)',
        'FrameMaker xm5.5.3L15a',
        'FrameMaker+SGML 5.5.6p145',
    ],
    'Adobe Illustrator': [
        'Adobe Illustrator',
        'Adobe Illustrator CS2',
        'Adobe Illustrator CS3',
        'Adobe Illustrator CS5',
        'Adobe Illustrator CS6',
        'Adobe Illustrator CS6 (Windows)',
    ],
    'Adobe InDesign': [
        'Adobe InDesign',
        'Adobe InDesign 2.0 CE',
        'Adobe InDesign CC (Macintosh)',
        'Adobe InDesign CC (Windows)',
        'Adobe InDesign CC 13.0 (Macintosh)',
        'Adobe InDesign CC 13.0 (Windows)',
        'Adobe InDesign CC 13.1 (Macintosh)',
        'Adobe InDesign CC 2014 (Macintosh)',
        'Adobe InDesign CC 2014 (Windows)',
        'Adobe InDesign CC 2015 (Macintosh)',
        'Adobe InDesign CC 2015 (Windows)',
        'Adobe InDesign CC 2017 (Macintosh)',
        'Adobe InDesign CC 2017 (Windows)',
        'Adobe InDesign CS (3.0.1)',
        'Adobe InDesign CS (3.0.1)(Infix Pro)',
        'Adobe InDesign CS2 (4.0)',
        'Adobe InDesign CS2 (4.0.2)',
        'Adobe InDesign CS2 (4.0.4)',
        'Adobe InDesign CS2 (4.0.5)',
        'Adobe InDesign CS3 (5.0)',
        'Adobe InDesign CS3 (5.0.1)',
        'Adobe InDesign CS3 (5.0.3)',
        'Adobe InDesign CS3 (5.0.4)',
        'Adobe InDesign CS3 (5.0.4)(Infix Pro)',
        'Adobe InDesign CS3 (5.0.5)',
        'Adobe InDesign CS4 (6.0)',
        'Adobe InDesign CS4 (6.0(Infix Pro(Infix Pro(Infix Pro(Infix Pro(Infix Pro)',
        'Adobe InDesign CS4 (6.0)(Infix Pro)',
        'Adobe InDesign CS4 (6.0)(Infix)',
        'Adobe InDesign CS4 (6.0.2)',
        'Adobe InDesign CS4 (6.0.3)',
        'Adobe InDesign CS4 (6.0.4)',
        'Adobe InDesign CS4 (6.0.5)',
        'Adobe InDesign CS4 (6.0.5)(Infix)',
        'Adobe InDesign CS4 (6.0.6)',
        'Adobe InDesign CS5 (7.0)',
        'Adobe InDesign CS5 (7.0)(Infix Pro)',
        'Adobe InDesign CS5 (7.0.3)',
        'Adobe InDesign CS5 (7.0.3)(Infix Pro)',
        'Adobe InDesign CS5 (7.0.4)',
        'Adobe InDesign CS5 (7.0.4)(Infix Pro)',
        'Adobe InDesign CS5 (7.0.5)',
        'Adobe InDesign CS5.5 (7.5)',
        'Adobe InDesign CS5.5 (7.5)(Infix Pro)',
        'Adobe InDesign CS5.5 (7.5.1)',
        'Adobe InDesign CS5.5 (7.5.1)(Infix Pro)',
        'Adobe InDesign CS5.5 (7.5.2)',
        'Adobe InDesign CS5.5 (7.5.3)',
        'Adobe InDesign CS6 (Macintosh)',
        'Adobe InDesign CS6 (Windows)',
        'InDesign: pictwpstops filter 1.0',
    ],
    'Adobe LiveCycle Designer': [
        'Adobe LiveCycle Designer',
        'Adobe LiveCycle Designer ES 8.2',
    ],
    'Adobe PageMaker': [
        'Adobe PageMaker',
        'Adobe PageMaker 6.52',
        'Adobe PageMaker 7.0',
        'Adobe® PageMaker® 6.0',
    ],
    'Adobe PDF Library': [
        'Adobe PDF Library',
        'Adobe PDF Library 8.0 modified using iText 5.0.3_SNAPSHOT (c) 1T3XT BVBA',
        'Adobe PDF Library 8.0 modified using iText 5.0.3_SNAPSHOT',
        'Adobe PDF Library 8.0; modified using iText 5.0.3_SNAPSHOT (c) 1T3XT BVBA',
        'Adobe PDF Library 9.9',
    ],
    'Adobe Photoshop': [
        'Adobe Photoshop',
        'Adobe Photoshop 7.0',
        'Photoshop PDF Plug-in',
        'Photoshop PDF Plug-in 1.0',
    ],
    'AdobePS': [
        'AdobePS',
        'Adobe PostScript printer driver',
        'PostScript Printer Driver AdobePS',
        'PostScript Printer Driver AdobePS(R)',
        'PostScript(R) Printer Driver AdobePS',
        'PostScript(R) Printer Driver AdobePS(R) 8.5.1',
        'PostScript(R) Printer Driver AdobePS(R)',
        'Textures.: AdobePS',
        'Textures®: AdobePS',
        'Textures.: AdobePS 8.5.1',
        'Textures®: AdobePS 8.7.3 (301)',
        'Textures.: AdobePS 8.5.1',
        'Textures®: AdobePS 8.7.3',
        'Textures. AdobePS',
        'Textures® AdobePS',
        'Textures. AdobePS 8.5.1',
        'Textures® AdobePS 8.7.3 (301)',
        'Textures. AdobePS 8.5.1',
        'Textures® AdobePS 8.7.3',
    ],
    'Advanced PDF Repair': [
        'Advanced PDF Repair',
        'Advanced PDF Repair at http://www.datanumen.com/apdfr/',
        'Advanced PDF Repair: http://www.pdf-repair.com',
        'DataNumen PDF Repair v2.1',
        'DataNumen PDF Repair',
        'DPDFR',
        'www.pdf-repair.com',
        'www.datanumen.com/apdfr/',
    ],
    'AH CSS Formatter': [
        'AH CSS Formatter',
        'AH CSS Formatter V1.0',
        'AH CSS Formatter V6.0 MR2 for Linux64 : 6.0.2.5372 (2012/05/16 18:26JST)',
        'AH CSS Formatter V6.1 R1 for Linux64 : 6.1.5.11330 (2013/05/23 13:33JST)',
        'AH CSS Formatter V6.2 MR3 for Linux64 : 6.2.5.18171 (2014/08/04 16:28JST)',
        'AH CSS Formatter V6.2 MR4 for Linux64 : 6.2.6.18551 (2014/09/24 15:00JST)',
        'AH CSS Formatter V6.2 R1 for Linux64 : 6.2.2.15776 (2014/02/27 18:51JST)',
        'AH CSS Formatter V6.2 R1 for Linux64 : 6.2.2.15776 (2014/02/27 18:51JST)',
    ],
    'AH XSL Formatter': [
        'AH XSL Formatter',
        'AH XSL Formatter V1.0',
        'AH XSL Formatter V6.0 MR5a for Windows',
        'AH XSL Formatter V6.0 MR5a for Windows : 6.0.6.7873',
        'AH XSL Formatter V6.0 MR5a for Windows : 6.0.6.7873 (2012/10/30 11:18JST)',
        'XSL Formatter V3.2 MR3',
        'XSL Formatter V3.4 MR3 (3,4,2006,0314) for Windows',
        'XSL Formatter V3.4 MR3 (3,4,2006,0314) for Windows(Infix)',
        'XSL Formatter V4.3 R1 (4,3,2008,0424) for Linux',
        'XSL Formatter V4.3 R1 (4,3,2008,0424) for Linux(Infix Pro)',
    ],
    'Antenna House': [
        'Antenna House',
        'Antenna House PDF Output Library',
        'Antenna House PDF Output Library 6.2.469',
        'Antenna House PDF Output Library 6.2.469 (Linux64)',
    ],
    'Apache FOP': [
        'Apache FOP',
        'Apache FOP Version 1.0',
    ],
    'A-PDF Merger': [
        'A-PDF Merger',
    ],
    'Apple iBooks': [
        'Apple iBooks',
        'iBooks',
        'iBooks Author',
    ],
    'Apple Keynote': [
        'Apple Keynote',
        'Apple Keynote 3.0.2',
        'Apple Keynote 4.0.1',
        'Apple Keynote 5.0',
    ],
    'Arbortext': [
        'Arbortext',
        'Arbortext Advanced Print Publisher',
        'Arbortext Advanced Print Publisher 11.0.34',
        'Arbortext Advanced Print Publisher 11.0.3433/W Unicode',
        'Arbortext Advanced Print Publisher 9.0.114/W Unicode',
        'Arbortext Advanced Print Publisher 9.0.222/W',
        'Arbortext Advanced Print Publisher 9.0.223/W Unicode',
        'Arbortext Advanced Print Publisher 9.1.405/W Unicode',
        'Arbortext Advanced Print Publisher 9.1.406/W Unicode',
        'Arbortext Advanced Print Publisher 9.1.500/W Unicode(Infix Pro)',
    ],
    'BCL PostScript Driver': [
        'BCL PostScript driver',
        'BCL PostScript Driver',
    ],
    'Boxoft Image To PDF': [
        'Boxoft Image To PDF',
    ],
    'Brother Printer': [
        'Brother Printer',
        'TW-Brother',
        'TW-Brother DCP-7040',
    ],
    'Cairo': [
        'Cairo',
        'cairo 1.10.0 (http://cairographics.org)',
        'cairo 1.14.6 (http://cairographics.org)',
        'cairo 1.14.8 (http://cairographics.org)',
        'cairo 1.2.3 (http://cairographics.org)',
        'cairo 1.2.3',
        'cairo 1.22.3 (http://cairographics.org)',
        'cairo 1.22.3',
        'cairo 1.22.33 (http://cairographics.org)',
        'cairo 1.22.33',
        'cairo 1.9.5 (http://cairographics.org)',
        'cairo 1.9.5 (http://cairographics.org)',
        'cairo 1.9.5',
        'cairo 11.2.3 (http://cairographics.org)',
        'cairo 11.2.3',
        'cairo 11.2.33 (http://cairographics.org)',
        'cairo 11.2.33',
        'cairo 11.22.3 (http://cairographics.org)',
        'cairo 11.22.3',
        'cairo 11.22.33 (http://cairographics.org)',
        'cairo 11.22.33',
    ],
    'Calibre': [
        'calibre',
        'CALIBRE',
        'calibre (0.9.42) [http://calibre-ebook.com]',
        'calibre (0.9.8) [http://calibre-ebook.com]',
        'calibre (1.2.3) [http://calibre-ebook.com]',
        'calibre (1.2.3) [https://calibre-ebook.com]',
        'calibre (1.2.3)',
        'calibre (1.22.33) [http://calibre-ebook.com]',
        'calibre (1.22.33) [https://calibre-ebook.com]',
        'calibre (1.22.33)',
        'calibre (1.31.0) [http://calibre-ebook.com]',
        'calibre (1.31.0) [https://calibre-ebook.com]',
        'calibre (1.48.0) [http://calibre-ebook.com]',
        'calibre (11.2.3) [http://calibre-ebook.com]',
        'calibre (11.2.3) [https://calibre-ebook.com]',
        'calibre (11.2.3)',
        'calibre (11.2.33) [http://calibre-ebook.com]',
        'calibre (11.2.33) [https://calibre-ebook.com]',
        'calibre (11.2.33)',
        'calibre (11.22.3) [http://calibre-ebook.com]',
        'calibre (11.22.3) [https://calibre-ebook.com]',
        'calibre (11.22.3)',
        'calibre (11.22.33) [http://calibre-ebook.com]',
        'calibre (11.22.33) [https://calibre-ebook.com]',
        'calibre (11.22.33)',
        'calibre (2.80.0) [http://calibre-ebook.com]',
        'calibre (2.80.0) [https://calibre-ebook.com]',
        'calibre (2.83.0) [http://calibre-ebook.com]',
        'calibre (2.83.0) [https://calibre-ebook.com]',
        'calibre (2.83.0)',
        'calibre (3.1.1) [http://calibre-ebook.com]',
        'calibre (3.1.1) [https://calibre-ebook.com]',
        'calibre 0.9.27 [http://calibre-ebook.com]',
        'calibre 1.0.0 [http://calibre-ebook.com]',
        'calibre 1.11.0 [http://calibre-ebook.com]',
        'calibre 1.2.3 [http://calibre-ebook.com]',
        'calibre 1.2.3 [https://calibre-ebook.com]',
        'calibre 1.2.3',
        'calibre 1.21.0 [http://calibre-ebook.com]',
        'calibre 1.22.33 [http://calibre-ebook.com]',
        'calibre 1.22.33 [https://calibre-ebook.com]',
        'calibre 1.22.33',
        'calibre 1.5.0 [http://calibre-ebook.com]',
        'calibre 11.2.3 [http://calibre-ebook.com]',
        'calibre 11.2.3 [https://calibre-ebook.com]',
        'calibre 11.2.3',
        'calibre 11.2.33 [http://calibre-ebook.com]',
        'calibre 11.2.33 [https://calibre-ebook.com]',
        'calibre 11.2.33',
        'calibre 11.22.3 [http://calibre-ebook.com]',
        'calibre 11.22.3 [https://calibre-ebook.com]',
        'calibre 11.22.3',
        'calibre 11.22.33 [http://calibre-ebook.com]',
        'calibre 11.22.33 [https://calibre-ebook.com]',
        'calibre 11.22.33',
        'calibre 2.35.0 [http://calibre-ebook.com]',
        'calibre 2.83.0 [http://calibre-ebook.com]',
        'calibre 2.83.0 [https://calibre-ebook.com]',
        'calibre 2.83.0',
        'calibre 3.2.0 [http://calibre-ebook.com]',
        'calibre 3.2.0 [https://calibre-ebook.com]',
        '[https://calibre-ebook.com]',
        '[http://calibre-ebook.com]',
        'https://calibre-ebook.com',
        'http://calibre-ebook.com',
    ],
    'Chromium': [
        'Chromium',
    ],
    'DocBook': [
        'DocBook XSL Stylesheets V1.71.1',
        'DocBook XSL Stylesheets V1.77.1',
    ],
    'dvips': [
        'dvips',
        'dvips 5.83 Copyright 1998 Radical Eye Software',
        'dvips(k) 5.86 Copyright 1999 Radical Eye Software',
        'dvips(k) 5.86d Copyright 1999 Radical Eye Software',
        'dvips(k) 5.92b Copyright 2002 Radical Eye Software',
        'dvips(k) 5.95a Copyright 2005 Radical Eye Software',
        'dvips(k) 5.95b Copyright 2005 Radical Eye Software',
        'dvips(k) 5.96.1 Copyright 2007 Radical Eye Software',
        'dvips(k) 5.99 Copyright 2010 Radical Eye Software',
        'dvips(k) 5.993 Copyright 2013 Radical Eye Software',
        'dvips(k)',
        'dvipsk 5.58f Copyright 1986, 1994 Radical Eye Software',
        'DVIPSONE 2.2.4  http://www.YandY.com',
    ],
    'Epson Printer': [
        'Epson Printer',
        'EPSON CX5900/CX6000/DX6000',
        'EPSON NX410/SX410/TX410',
        'EPSON Perfection 3170',
    ],
    'FinePrint pdfFactory': [
        'FinePrint pdfFactory',
    ],
    'FineReader': [
        'FINEREADER',
    ],
    'Foxit': [
        'Foxit',
        '(Foxit Advanced PDF Editor)',
        'Foxit Advanced PDF Editor',
        'ÿþM(Foxit Advanced PDF Editor)',
    ],
    'Fujitsu Printer': [
        'Fujitsu Printer',
        'ScanSnap Manager',
        'ScanSnap Manager #iX500',
        'ScanSnap Manager #S1300',
    ],
    'Ghostscript': [
        'Ghostscript',
        'GPL Ghostscript',
        'GPL Ghostscript 9.10',
        'GPL Ghostscript 9.07',
        'GPL Ghostscript 1.2',
        'GPL Ghostscript 1.2.3',
    ],
    'groff': [
        'groff',
        'groff version 1.18',
        'groff version 1.18.1',
    ],
    'gscan2pdf': [
        'gscan2pdf',
        'gscan2pdf v1.0.1',
    ],
    'HP Printer': [
        'HP Printer',
        'WIA-HP psc',
        'WIA-HP psc 1300',
    ],
    'HTML Tidy': [
        'HTML Tidy',
        'HTML Tidy for FreeBSD',
        'HTML Tidy for FreeBSD (vers 7 December 2008)',
        'HTML Tidy for FreeBSD (vers 7 December 2008), see www.w3.org',
        'HTML Tidy for Mac OS X',
        'HTML Tidy for Mac OS X (vers 1st December 2004)',
        'HTML Tidy for Mac OS X (vers 1st December 2004), see www.w3.org',
    ],
    'Image2PDF': [
        'Image2PDF',
        'Image2PDF Command Line software',
    ],
    'Infix Pdf Editor': [
        'Infix Pdf Editor',
        'Infix Pro',
        '(Infix Pro)',
        'Iceni Technology Products',
        'Iceni Technology',
    ],
    'iText': [
        'iText',
        'iText 4.2.0 by 1T3XT',
        'iText 1.2.3 by 1T3XT',
        'iText 1.22.3 by 1T3XT',
        'iText 1.22.33 by 1T3XT',
        'iText 11.2.3 by 1T3XT',
        'iText 11.2.33 by 1T3XT',
        'iText 11.22.3 by 1T3XT',
        'iText 11.22.33 by 1T3XT',
    ],
    'Kingsoft WPS Office': [
        'KSOffice',
        'Kingsoft Office',
        'Kingsoft WPS Office',
        'WPS Office',
        'WPS Office 个人版',
    ],
    'Microsoft Trident': [
        'MSHTML 5.00.3502.5390',
        'MSHTML 6.00.2800.1126',
    ],
    'Microsoft PowerPoint': [
        'PowerPoint',
        'Acrobat PDFMaker 6.0 for PowerPoint',
        'Acrobat PDFMaker 7.0.5 for PowerPoint',
        'Acrobat PDFMaker 8.1 for PowerPoint',
        'Adobe Acrobat PDFMaker 6.0 for PowerPoint',
        'Adobe Acrobat PDFMaker 7.0.5 for PowerPoint',
        'Adobe Acrobat PDFMaker 8.1 for PowerPoint',
        'Microsoft Office PowerPoint 2007',
        'Microsoft Office PowerPoint',
        'Microsoft PowerPoint - [hack_3.ppt]',
        'Microsoft PowerPoint - [meow meow]',
        'Microsoft PowerPoint - [WM4]',
        'Microsoft PowerPoint',
        'Microsoft PowerPoint',
        'Microsoft® Office PowerPoint',
        'Microsoft® Office PowerPoint® 2007',
        'Microsoft® PowerPoint® 2013',
    ],
    'Microsoft Publisher': [
        'Microsoft Publisher',
        'Microsoft® Publisher',
        'Microsoft® Publisher 2010',
    ],
    'Microsoft Word': [
        'Microsoft Word',
        'Acrobat PDFMaker 10.0 for Word',
        'Acrobat PDFMaker 10.1 for Word',
        'Acrobat PDFMaker 11 for Word',
        'Acrobat PDFMaker 15 for Word',
        'Acrobat PDFMaker 18 for Word',
        'Acrobat PDFMaker 5.0 for Word',
        'Acrobat PDFMaker 6.0 for Word',
        'Acrobat PDFMaker 7.0 for Word',
        'Acrobat PDFMaker 7.0.5 for Word',
        'Acrobat PDFMaker 8.1 for Word',
        'Acrobat PDFMaker 9.0 for Word',
        'Adobe Acrobat PDFMaker 10.1 for Word',
        'Adobe Acrobat PDFMaker 11 for Word',
        'Adobe Acrobat PDFMaker 6.0 for Word',
        'Adobe Acrobat PDFMaker 7.0 for Word',
        'Adobe Acrobat PDFMaker 7.0.5 for Word',
        'C:\ProgramFiles\Microsoft Office\OFFICE10\WINWORD.EXE',
        'C:\ProgramFiles\Microsoft Office\OFFICE11\WINWORD.EXE',
        'C:\ProgramFiles\Microsoft Office\OFFICE12\WINWORD.EXE',
        'D:\ProgramFiles\Microsoft Office\OFFICE10\WINWORD.EXE',
        'D:\ProgramFiles\Microsoft Office\OFFICE11\WINWORD.EXE',
        'D:\ProgramFiles\Microsoft Office\OFFICE12\WINWORD.EXE',
        'E:\ProgramFiles\Microsoft Office\OFFICE10\WINWORD.EXE',
        'E:\ProgramFiles\Microsoft Office\OFFICE11\WINWORD.EXE',
        'E:\ProgramFiles\Microsoft Office\OFFICE12\WINWORD.EXE',
        'F:\ProgramFiles\Microsoft Office\OFFICE10\WINWORD.EXE',
        'F:\ProgramFiles\Microsoft Office\OFFICE11\WINWORD.EXE',
        'F:\ProgramFiles\Microsoft Office\OFFICE12\WINWORD.EXE',
        'G:\ProgramFiles\Microsoft Office\OFFICE10\WINWORD.EXE',
        'G:\ProgramFiles\Microsoft Office\OFFICE11\WINWORD.EXE',
        'G:\ProgramFiles\Microsoft Office\OFFICE12\WINWORD.EXE',
        'Microsoft Word - Check Out The Most Amazing Wallpapers.doc',
        'Microsoft Word 2000/2002',
        'Microsoft Word 9.0',
        'Microsoft Word',
        'Microsoft Word: cgpdftops CUPS filter(Infix Pro)',
        'Microsoft® Office Word 2007 (Beta)',
        'Microsoft® Office Word 2007',
        'Microsoft® Word 2010 Trial',
        'Microsoft® Word 2010',
        'Microsoft® Word 2013',
        'Microsoft® Word 2016',
        'Microsoft® Word Starter 2010',
        'Socket_quickref - Microsoft Word',
        'WINWORD.EXE',
    ],
    'Mozilla PostScript': [
        'Mozilla PostScript',
        'Mozilla PostScript module',
        'Mozilla PostScript module (rv:1.7.12/2005092000)',
    ],
    'PaperPort': [
        'PaperPort',
        'PaperPort http://www.scansoft.com',
        'http://www.scansoft.com',
        'www.scansoft.com',
    ],
    'PDFBox': [
        'PDFBox',
        'PDFBox.org',
    ],
    'PdfCompressor': [
        'PdfCompressor 3.1.34',
    ],
    'PDF Creator': [
        'PDF Creator Pilot 3.9.1094.0',
        'PDF Creator Pilot  program',
        'PDF Creator Plus 4.0 - http://www.peernet.com',
        'PDFCreator Version 0.9.3',
        'www.peernet.com',
    ],
    'PDFelement': [
        'PDFelement',
        'PDFelement 6',
        'PDFelement 6 Professional',
    ],
    'PDFium': [
        'PDFium',
    ],
    'PDFMerge': [
        'PDFMerge',
        'PDFMerge!',
        'PDFMerge! (http://www.pdfmerge.com)',
        'PDFMerge! http://www.pdfmerge.com',
        'PDFMerge (http://www.pdfmerge.com)',
        'PDFMerge http://www.pdfmerge.com',
        'www.pdfmerge.com',
    ],
    'PDF Nomad': [
        'PDF Nomad',
    ],
    'pdfresizer': [
        'pdfresizer',
        'pdfresizer.com',
        'Edited with pdfresizer.com',
    ],
    'PDFsam': [
        'PDFsam',
        'PDFsam Basic v3.1.0.RELEASE',
        'PDFsam Basic v3.3.0',
        'PDFsam Basic v3.3.2',
        'pdfsam-console (Ver. 1.1.4e)',
        'pdfsam-console (Ver. 1.1.5e)',
        'pdfsam-console (Ver. 2.0.2e)',
        'pdfsam-console (Ver. 2.0.5e)',
        'pdfsam-console (Ver. 2.3.0e)',
        'pdfsam-console (Ver. 2.4.0e)',
        'pdfsam-console (Ver. 2.4.1e)',
        'pdfsam-console',
    ],
    'PDFsharp': [
        'PDFsharp',
        'PDFsharp 1.2.1269-g',
        'PDFsharp 1.31.1789-g',
        'PDFsharp 1.32.2608-g',
        'PDFsharp 1.2.1269-g (www.pdfsharp.com)',
        'PDFsharp 1.31.1789-g (www.pdfsharp.com)',
        'PDFsharp 1.32.2608-g (www.pdfsharp.net)',
        'www.pdfsharp.net',
    ],
    'pdfTeX': [
        'pdfTeX',
        'pdftex',
        'pdfTeX-1.40.16',
        'pdfTeX-1.2.3',
        'pdfTeX-1.22.3',
        'pdfTeX-1.22.33',
        'pdfTeX-11.2.3',
        'pdfTeX-11.2.33',
        'pdfTeX-11.22.3',
        'pdfTeX-11.22.33',
        'This is pdfTeX Version 3.14',
        'This is pdfTeX Version 3.14159265-2.6-1.4',
        'This is pdfTeX, Version 3.14',
        'This is pdfTeX, Version 3.14159265-2.6-1.4',
    ],
    'pdftk': [
        'pdftk 1.41 - www.pdftk.com',
        'pdftk 1.41',
        'pdftk 1.44 - www.pdftk.com',
        'pdftk 1.44',
        'pdftk 2.01 - www.pdftk.com',
        'pdftk 2.01',
        'pdftk 2.02 - www.pdftk.com',
        'pdftk 2.02',
        'pdftk',
        'www.pdftk.com',
    ],
    'PDFWriters': [
        'PDFWriters',
        'PDFWriters Suite',
    ],
    'PowerPDF': [
        'PowerPDF',
    ],
    'PrimoPDF': [
        'PrimoPDF',
        'PrimoPDF http://www.primopdf.com',
        'http://www.primopdf.com',
        'www.primopdf.com',
    ],
    'PrinceXML': [
        'PrinceXML',
        'Prince 1.22 (www.princexml.com)',
        'Prince 1.22 www.princexml.com',
        'Prince 1.22',
        'Prince 11.0 (www.princexml.com)',
        'Prince 11.0 www.princexml.com',
        'Prince 11.0',
        'Prince 11.22 (www.princexml.com)',
        'Prince 11.22 www.princexml.com',
        'Prince 11.22',
        'Prince 6.0 (www.princexml.com)',
        'Prince 6.0 www.princexml.com',
        'Prince 6.0',
        'www.princexml.com',
    ],
    'Print2PDF': [
        'Print2PDF',
        'Print2PDF 5.0.06.0426',
        'Print2PDF 5.0.06.0426 by Software602',
    ],
    'PScript': [
        'PScript5',
        'Pscript.dll Version 5.0',
        'PSCRIPT.DRV Version 4.0',
        'PScript5.dll Version 1.2.3',
        'PScript5.dll Version 1.22.3',
        'PScript5.dll Version 1.22.33',
        'PScript5.dll Version 11.2.3',
        'PScript5.dll Version 11.2.33',
        'PScript5.dll Version 11.22.3',
        'PScript5.dll Version 11.22.33',
        'PScript5.dll Version 5.2',
        'PScript5.dll Version 5.2.(Infix Pro(Infix Pro)',
        'PScript5.dll Version 5.2.2',
        'PScript5.dll Version 5.2.2(Infix Pro)',
        'PScript5.dll',
    ],
    'QuarkXPress': [
        'QuarkXPress',
        'QuarkXPress™',
        'QuarkXPress 8.02',
        'QuarkXPress 8.1.6.2',
        'QuarkXPressª 4.1: LaserWriter 8 8.6.5',
        'QuarkXPressª 4.1: LaserWriter 8 8.7',
        'QuarkXPressª: LaserWriter 8 8.6.5',
        'QuarkXPressâ—¢: LaserWriter 8 8.7.1',
        'QuarkXPress Passportª: PSPrinter 8.3.1',
        'QuarkXPress: pictwpstops filter 1.0',
        'QuarkXPress(tm) 4.1',
        'QuarkXPress(tm) 6.0',
        'QuarkXPress(tm) 6.5',
        'QuarkXPress(tm) 6.52',
        'quark1user',
        'quark10user',
        'quark65user',
    ],
    'ScanToPDF': [
        'ScanToPDF',
        'ScanToPDF 3.1.4.0',
        'ScanToPDF 3.1.4.0 (http://www.scantopdf.co.uk)',
        'www.scantopdf.co.uk',
    ],
    'SkiaPDF': [
        'SkiaPDF',
        'skiapdf',
        'Skia/PDF',
        'Skia PDF',
    ],
    'LaTeX': [
        'latex',
        'LaTeX',
        'LaTeX with hyperref package',
    ],
    'TeX': [
        'tex',
        'TeX',
        'TeX output 2003.02.20:0404',
        'TeX output 2005.08.28:1646',
        'TeX output 2008.06.18:1321',
        ' TeX output 2003.02.20:0404',
        ' TeX output 2005.08.28:1646',
        ' TeX output 2008.06.18:1321',
    ],
    'tiff2ps': [
        'tiff2ps',
    ],
    'ToPDF.com': [
        'ToPDF.com',
        'topdf.com',
    ],
    'TopLeaf': [
        'TopLeaf',
        'TopLeaf 8.0.0',
        'TopLeaf 8.0.017',
        'TopLeaf XML 8.0.0',
        'TopLeaf XML 8.0.017',
        'TopLeaf XML',
        'Turn-Key Systems',
        'Turn-Key Systems Pty Ltd',
        'Turn-Key Systems Proprietary Ltd',
        'Turn-Key Systems Proprietary Limited',
        'Turn-Key Systems TopLeaf',
        'Turn-Key Systems TopLeaf 8.0.0',
        'Turn-Key Systems TopLeaf 8.0.017',
        'Turn-Key Systems TopLeaf XML 8.0.0',
        'Turn-Key Systems TopLeaf XML 8.0.017',
        'Turn-Key Systems TopLeaf XML',
    ],
    'Tracker PDF-Tools': [
        'Tracker PDF-Tools',
        'Trackers PDF-Tools',
        "Tracker's PDF-Tools",
    ],
    'UNKNOWN': [
        'UNKNOWN',
        'Unknown',
        'UnknownApplication',
    ],
    'VTeX PDF Tools': [
        'VTeX PDF Tools',
    ],
    'Win2PDF': [
        'Win2PDF',
        'Win2PDF 2.80',
        'Win2PDF 2.80 http://www.daneprairie.com',
        'http://www.daneprairie.com',
        'www.daneprairie.com',
    ],
    'wpCubed wPDF': [
        'wpCubed wPDF',
        'wPDF',
        'wPDF by wpCubed',
        'wPDF by wpCubed GmbH',
    ],
    'XEP': [
        'XEP',
        'XEP 4.5',
        'XEP 4.5 build 20060313',
    ],
    'XeTeX': [
        'XeTeX',
        'XeTeX output',
        'XeTeX output 2011.11.24:1058',
        ' XeTeX output 2011.11.24:1058',
    ],
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

    def test_does_not_canonicalize_non_publishers(self):
        for given_non_publisher in [
            '',
            'foo',
            'then press real hard',
            'publishing is a thing',
            'the academic press probably applies academical weight',
        ]:
            with self.subTest(given=given_non_publisher):
                actual = _canonicalize_publisher(given_non_publisher)
                self.assertEqual(given_non_publisher, actual)


class TestCanonicalizeLanguage(TestCase):
    def test_canonicalize_language(self):
        for canonical, equivalent_values in LANGUAGE_CANONICAL_EQUIVALENTS.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given_expected=(equivalent_value, canonical)):
                    actual = _canonicalize_language(equivalent_value)
                    self.assertEqual(canonical, actual)

    def test_does_not_canonicalize_non_languages(self):
        for given_non_language in [
            '',
            'foo',
            'en katt slickade på osten',
            'ovanstående text är på svenska',
            'det var en svensk katt',
            'new english review',
            'english is a language',
        ]:
            with self.subTest(given=given_non_language):
                actual = _canonicalize_language(given_non_language)
                self.assertEqual(given_non_language, actual)


class TestCanonicalizeCreatortool(TestCase):
    def test_canonicalize_creatortool(self):
        for canonical, equivalent_values in CREATORTOOL_CANONICAL_EQUIVALENTS.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given_expected=(equivalent_value, canonical)):
                    actual = _canonicalize_creatortool(equivalent_value)
                    self.assertEqual(canonical, actual)

    def test_does_not_canonicalize_non_creatortools(self):
        for given_non_creatortool in [
            '',
            'foo',
        ]:
            with self.subTest(given=given_non_creatortool):
                actual = _canonicalize_language(given_non_creatortool)
                self.assertEqual(given_non_creatortool, actual)


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

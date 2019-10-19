#!/usr/bin/env python3
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

import os

"""
Writes sample text to files using different encodings.
"""

_SELF_DIRPATH = os.path.abspath(os.path.dirname(__file__))
DEST_DIRPATH = os.path.join(_SELF_DIRPATH, 'sample_textfiles')

# The Project Gutenberg EBook of Beowulf
#
# This eBook is for the use of anyone anywhere at no cost and with
# almost no restrictions whatsoever.  You may copy it, give it away or
# re-use it under the terms of the Project Gutenberg License included
# with this eBook or online at www.gutenberg.net
#
# Title: Beowulf
#        An Anglo-Saxon Epic Poem, Translated From The Heyne-Socin
#        Text by Lesslie Hall
# Release Date: July 19, 2005 [EBook #16328]
SAMPLE_TEXT = '''
BEOWULF.




I.

THE LIFE AND DEATH OF SCYLD.


{The famous race of Spear-Danes.}

          Lo! the Spear-Danes' glory through splendid achievements
          The folk-kings' former fame we have heard of,
          How princes displayed then their prowess-in-battle.

{Scyld, their mighty king, in honor of whom they are often called
Scyldings. He is the great-grandfather of Hrothgar, so prominent in the
poem.}

          Oft Scyld the Scefing from scathers in numbers
        5 From many a people their mead-benches tore.
          Since first he found him friendless and wretched,
          The earl had had terror: comfort he got for it,
          Waxed 'neath the welkin, world-honor gained,
          Till all his neighbors o'er sea were compelled to
       10 Bow to his bidding and bring him their tribute:
          An excellent atheling! After was borne him

{A son is born to him, who receives the name of Beowulf--a name afterwards
made so famous by the hero of the poem.}


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Source for the following text: http://www.heorot.dk/beowulf-rede-text.html

Listen! We --of the Spear-Danes      in the days of yore,
of those clan-kings--      heard of their glory.
how those nobles      performed courageous deeds.

Hwæt! Wé Gárdena      in géardagum
þéodcyninga      þrym gefrúnon·
hú ðá æþelingas      ellen fremedon.

------------------------------------------------------------------------------

Oft Scyld Scéfing      sceaþena þréatum	
Often Scyld, Scef's son,      from enemy hosts
monegum maégþum      meodosetla oftéah·	
from many peoples      seized mead-benches;
egsode Eorle      syððan aérest wearð	
and terrorised the fearsome Heruli      after first he was
féasceaft funden      hé þæs frófre gebád·	
found helpless and destitute,      he then knew recompense for that:-
wéox under wolcnum·      weorðmyndum þáh	
he waxed under the clouds,      throve in honours,
oð þæt him aéghwylc      þára ymbsittendra	
until to him each      of the bordering tribes
ofer hronráde      hýran scolde,	
beyond the whale-road      had to submit,
gomban gyldan·      þæt wæs gód cyning.	
and yield tribute:-      that was a good king!
'''


if not os.path.isdir(DEST_DIRPATH):
    try:
        os.makedirs(DEST_DIRPATH)
    except OSError as e:
        print('Unable to create destination directory; {!s}'.format(e))
        exit(1)


def write_alphanumeric_characters(out, encoding, num_chars=512):
    for i in range(num_chars):
        try:
            uni_char = str(i)
            if uni_char.isalnum():
                bytes_ = uni_char.encode(encoding)
                out.write(bytes_)
        except Exception as e:
            print('ERROR: {!s}'.format(e))
    out.write(b'\n')


def write_sample_text(out, encoding):
    try:
        bytes_ = SAMPLE_TEXT.encode(encoding, errors='ignore')
        out.write(bytes_)
    except Exception as e:
        print('ERROR: {!s}'.format(e))
        return


CODECS = ['ascii', 'cp437', 'cp858', 'cp1252', 'iso-8859-1', 'macroman',
          'utf-8', 'utf-16']

for codec in CODECS:
    _alnum_dest_path = os.path.join(DEST_DIRPATH, 'text_alnum_{}.txt'.format(codec))
    with open(_alnum_dest_path, 'wb') as fh:
        write_alphanumeric_characters(fh, codec, num_chars=512)

    _sampletext_dest_path = os.path.join(DEST_DIRPATH,
                                         'text_sample_{}.txt'.format(codec))
    with open(_sampletext_dest_path, 'wb') as fh:
        write_sample_text(fh, codec)

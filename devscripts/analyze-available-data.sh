#!/usr/bin/env bash

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

# DESCRIPTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Experimental script for finding expected field values in the output
# of 'autonameow --list-all'.  The idea is to better understand where
# "target values" might be found.
#
# Pass in one or more text files with comma-separated values.
# Expected fields:
# [absolute path],[publisher],[title],[edition],[author],[year]
#
# Each line corresponds to an actual file with expected field values.
#
# autonameow is started with the '--list-all' option and the file at
# [absolute path].  The results is grepped for the expected values;
# [publisher], [title], etc., printing any matches, to hopefully
# provide some insight in where the "target data" might come from ..
#
#
# EXAMPLE OUTPUT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Input file path: "/home/jonas/dev/projects/autonameow.git/test_files/4123.pdf"
# EXPECTED VALUES:
#    Author: "Bertrand Russell"
#   Edition: "1"
# Publisher: "feedbooks"
#     Title: "Mysticism and Logic and Other Essays"
#      Year: "1918"
#
# MATCHES IN AUTONAMEOW OUTPUT:
# Author        (NO MATCHES)
# Edition       (NO MATCHES)
# Publisher     analyzer.document.publisher               ::  FeedBooks
# Publisher     generic.metadata.publisher                ::  FeedBooks
# Title         analyzer.document.title                   ::  Mysticism and Logic and Other Essays
# Title         generic.contents.text                     ::  Mysticism and Logic and Other Essays
# Title         generic.metadata.title                    ::  Mysticism and Logic and Other Essays
# Title         generic.metadata.title                    ::  Mysticism and Logic and Other Essays
# Title         extractor.metadata.exiftool.PDF:Title     ::  Mysticism and Logic and Other Essays
# Title         extractor.text.pdftotext.full             ::  Mysticism and Logic and Other Essays
# Year          (NO MATCHES)
#
#
# Input file path: "/home/jonas/dev/projects/autonameow.git/test_files/Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf"
# EXPECTED VALUES:
#    Author: "Charles Darwin"
#   Edition: "6"
# Publisher: "feedbooks"
#     Title: "On the Origin of Species"
#      Year: "1872"
#
# MATCHES IN AUTONAMEOW OUTPUT:
# Author        (NO MATCHES)
# Edition       analyzer.document.title                     ::  On the Origin of Species, 6th Edition
# Edition       analyzer.filename.edition                   ::  6
# Edition       extractor.filesystem.filetags.description   ::  Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition
# Edition       generic.contents.text                       ::  On the Origin of Species, 6th Edition
# Edition       generic.metadata.description                ::  Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition
# Edition       generic.metadata.edition                    ::  6
# Edition       generic.metadata.title                      ::  On the Origin of Species, 6th Edition
# Edition       generic.metadata.title                      ::  On the Origin of Species, 6th Edition
# Edition       extractor.metadata.exiftool.File:FileName   ::  Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf
# Edition       extractor.metadata.exiftool.PDF:Title       ::  On the Origin of Species, 6th Edition
# Edition       extractor.text.pdftotext.full               ::  On the Origin of Species, 6th Edition
# Edition       extractor.filesystem.xplat.basename.full    ::  Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition.pdf
# Edition       extractor.filesystem.xplat.basename.prefix  ::  Charles+Darwin+-+On+the+Origin+of+Species%2C+6th+Edition
# Publisher     analyzer.document.publisher                 ::  FeedBooks
# Publisher     generic.metadata.publisher                  ::  FeedBooks
# Title         analyzer.document.title                     ::  On the Origin of Species, 6th Edition
# Title         generic.contents.text                       ::  On the Origin of Species, 6th Edition
# Title         generic.metadata.title                      ::  On the Origin of Species, 6th Edition
# Title         generic.metadata.title                      ::  On the Origin of Species, 6th Edition
# Title         extractor.metadata.exiftool.PDF:Title       ::  On the Origin of Species, 6th Edition
# Title         extractor.text.pdftotext.full               ::  On the Origin of Species, 6th Edition
# Year          (NO MATCHES)


set -o noclobber -o nounset -o pipefail

# Substitute path to the runner script.
AUTONAMEOW="autonameow"

print_autonameow_matches()
{
    while IFS=$'\n' read -r line
    do
        printf '%-13.13s %s\n' "$1" "$line"
    done <<< "$2"
}

main()
{
    # Read each lines comma-separated values.
    while IFS=',' read -r abspath publisher title edition author year
    do
        if [ -z "$abspath" ]
        then
            printf '[WARNING] Skipped -- "abspath" is unset\n\n' >&2
            continue
        fi
        if [ ! -f "$abspath" ]
        then
            printf '[WARNING] Skipped -- "abspath" is not a file: "%s"\n\n' "$abspath" >&2
            continue
        fi

        printf 'Input file path: "%s"\n' "$abspath"
        printf 'EXPECTED VALUES:\n'
        printf '   Author: "%s"\n'       "$author"
        printf '  Edition: "%s"\n'       "$edition"
        printf 'Publisher: "%s"\n'       "$publisher"
        printf '    Title: "%s"\n'       "$title"
        printf '     Year: "%s"\n\n'     "$year"

        autonameow_output="$(${AUTONAMEOW} --batch --list-all --dry-run -- "$abspath" 2>/dev/null |
                             grep -v 'Would have renamed' | # hacky
                             grep -v '    ->  ' |           # hacky
                             grep -v 'because the current name is the' | # hacky
                             grep -v 'FileObject absolute path' | # too obvious ..
                             grep -v 'FileObject basename' |      # too obvious ..
                             grep -v -- "$abspath")"

        GREP_OPTS='-i --color=always'
        actual_publisher="$(grep $GREP_OPTS -- "$publisher" <<< "$autonameow_output")"
        actual_title="$(grep $GREP_OPTS -- "$title" <<< "$autonameow_output")"
        actual_edition="$(grep $GREP_OPTS -- "edition" <<< "$autonameow_output")"
        actual_author="$(grep $GREP_OPTS -- "$author" <<< "$autonameow_output")"
        actual_year="$(grep $GREP_OPTS -- "$year" <<< "$autonameow_output")"

        NO_MATCH_STR='(NO MATCHES)'
        printf 'MATCHES IN AUTONAMEOW OUTPUT:\n'
        print_autonameow_matches 'Author'    "${actual_author:-${NO_MATCH_STR}}"
        print_autonameow_matches 'Edition'   "${actual_edition:-${NO_MATCH_STR}}"
        print_autonameow_matches 'Publisher' "${actual_publisher:-${NO_MATCH_STR}}"
        print_autonameow_matches 'Title'     "${actual_title:-${NO_MATCH_STR}}"
        print_autonameow_matches 'Year'      "${actual_year:-${NO_MATCH_STR}}"
        printf '\n\n'

    done < "$1"
}


for arg in "$@"
do
    if [ ! -f "$arg" ]
    then
        echo "Not a file: \"${arg}\""
        continue
    elif [ ! -r "$arg" ]
    then
        echo "Not a readable file: \"${arg}\""
        continue
    else
        main "$arg"
    fi
done


exit $?



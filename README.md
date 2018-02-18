`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

__`autonameow` does automatic renaming of files__

The primary goal is to reduce the overhead and manual work required to
apply a strict file naming convention uniformly and consistently.

#### PLEASE NOTE
__This software is still in early stages of development --- NOT READY FOR USE!__

--------------------------------------------------------------------------------

`autonameow` is written for __Python 3.5+__, targeting __Linux__ and
__MacOS__.

Support for additional platforms will probably be added at some future time.

~~(Both Android and Windows already seems to work good enough with some
tweaking and/or inconveniences)~~

Don't expect `autonameow` to run on anything but the targeted platforms, for
now.


Current Features
----------------

* __Rule-based Renaming__
    * __Conditions__ are evaluated in order to to determine whether to use a
      certain rule for a given file
    * __Name Template__ rule-specific file name template to use for the new file name
    * __Sources__ specifies which data is used to populate the name template
    * Rules are ranked by score, weight and a "bias"
    * Rules can be set to allow failed conditions, which allows powerful
      layering of more or less "targeted" rules.
* __ISBN Number__ Extraction and Metadata Lookup
    * Very powerful renaming of ebooks
    * Combines information from several sources to determine possible candidate data
    * Extract ISBN numbers from various ebooks and query metadata APIs
    * Fuzzy de-duplication of ISBN metadata
* __Metadata Extraction__ from textual contents
    * Fuzzy extraction of date/time-information, possible titles, etc.
* __Text Extraction__ from plain text, epub, pdf and rtf files
* __Metadata extraction from a lot of file formats__ (using [exiftool][2])
* Metadata extraction from file names
* Robust extraction of information from file names following the [filetags][1] naming scheme
* __Caching__ of slow operation, like querying third-party servers or extracting large amounts of text
* __Batch Mode__ for completely hands-off operating, suitable for scripting
* __Timid Mode__ prompts prior to renaming files with a preview.
* Human name parsing and formatting
* Regex Replacement Patterns allows final tweaking of the results
* Configuration through a YAML config file
* Global ignore patterns using globs
* Sane built-in default ignore patterns.
* Recursive mode


Planned/WIP Features
--------------------

* Smarter ranking of extracted data
* Smarter de-duplication of extracted data
* Improvements to all kinds of "decision making"
* Improved filtering of extracted data
* __Interactive Mode__
* __Automagic Mode__ "try-hard mode" for cases where rules do not apply or data
  specified in rules is not available
* Additional content extractors
* Additional metadata extractors
* Support for additional third-party metadata providers
* *Run completely "hands-off" and always do "the right thing" . .*


Installing
==========
If you want to use `autonameow`, __please wait for the first stable release__;
version `v1.0.0`.

Don't feel like waiting?  See [`install.md`](./install.md) for a *(temporary)*
guide to installing under Linux and MacOS.


Running
=======
Use the wrapper script `bin/autonameow.sh` to start `autonameow`.


Documentation
=============
The wiki is not be updated and does not reflect the current state of the
project. I simply don't have time to keep the documentation in sync with
frequent and non-trivial changes to the software.

The project was for a period of time developed as part of the course
"`1DV430` -- Individual Software Development Project", given at
[Linnaeus University](https://lnu.se/en/) as part of the
"[Software Development and Operations](https://udm-devops.se/)" programme.

The course work began at version `v0.3.0`
([commit](https://github.com/jonasjberg/autonameow/commit/cbe439104813d83ee5a6274eed0943433955b59c))
and ended with version `v0.4.0`
([commit](https://github.com/jonasjberg/autonameow/commit/da494350dca4f99157cc8f7541f92ca8d7f3daf1))

See the [project wiki](https://github.com/jonasjberg/autonameow/wiki) for
documentation related to this coursework.


License
=======
`autonameow` is licensed under the *GNU GPL version 2*.

> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <http://www.gnu.org/licenses/>.

Refer to `LICENSE.txt` for the full license.
Also available [here](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt).


[1]: https://github.com/novoid/filetags
[2]: https://www.sno.phy.queensu.ca/~phil/exiftool/

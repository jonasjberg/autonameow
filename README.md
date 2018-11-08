`autonameow`
============
Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>  
Source repository: <https://github.com/jonasjberg/autonameow>

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

* __Rule-based renaming__
    * __Conditions__ are evaluated in order to determine whether to use a
      certain rule for a given file
    * __Name template__ has placeholder fields that will be populated with
      suitable data
    * __Sources__ specifies which data is used to populate which placeholder
      fields in the name template
    * Rules are ranked by score, relative score and a "bias"
    * Rules can be set to allow failed conditions, which allows powerful
      layering of more or less "targeted" rules
* __Text extraction__
    * From various text formats; `epub`, markdown, `pdf`, `rtf`, `txt`, etc.
    * From images using [tesseract][6] to do OCR
    * Filtering and miscellaneous processing of extracted text
* __Metadata extraction from a lot of file formats__
    * Uses various third-party binaries such as [exiftool][2], [pandoc][7], [jpeginfo][8], ..
    * Filtering and miscellaneous processing of raw metadata
    * Collected metadata is made accessible through a common mechanism
* Metadata extraction from textual contents
    * Fuzzy extraction of date/time-information, possible titles, etc.
* Metadata extraction from file names
* __ISBN number extraction and metadata lookup__
    * Facilitates powerful renaming of ebooks
    * Combines information from several sources to determine possible candidate data
    * Extract ISBN numbers from various ebooks and query metadata APIs
    * Fuzzy de-duplication of ISBN metadata
* Robust extraction of information from file names following the __[filetags][1] naming scheme__
* __Caching__ of slow operations, like querying third-party servers or extracting large amounts of text
* __Batch mode__ for completely hands-off operation, suitable for scripting
* __Timid mode__ prompts prior to renaming files with a preview
* Human name parsing and formatting
* Regex replacement patterns
* Configuration through a YAML config file
* Global ignore patterns using globs
* Sane built-in default ignore patterns
* Recursive mode
* [Extensive test suite][5]


Planned/WIP Features
--------------------

* Smarter ranking of extracted data
* Smarter de-duplication of extracted data
* Improvements to all kinds of "decision making"
* Improved filtering of extracted data
* Interactive mode
* __Automagic mode__ "try-hard mode" for cases where rules do not apply or data
  specified in rules is not available
* Additional content extractors
* Additional metadata extractors
* Support for additional third-party metadata providers
* Sane dependency management, packaging and installation
* Graphical User Interface (?)
* *Run completely "hands-off" and always do "the right thing" ..*

Refer to the [TODO-list][3] for planned features and changes.
Completed entries are listed [here][4].


Installing
==========
If you want to use `autonameow`, __please wait for the first stable release__;
version `v1.0.0`.

Don't feel like waiting?  See [`install.md`](./install.md) for a *(temporary)*
guide to installing under Linux and MacOS.


Running
=======
Use the wrapper script `bin/autonameow` to start `autonameow`.
Pass `--help` to get up-to-date usage information.


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
[3]: https://github.com/jonasjberg/autonameow/blob/master/TODO.md
[4]: https://github.com/jonasjberg/autonameow/blob/master/done.md
[5]: https://github.com/jonasjberg/autonameow/blob/master/tests/README.md
[6]: https://github.com/tesseract-ocr
[7]: https://pandoc.org
[8]: https://github.com/tjko/jpeginfo

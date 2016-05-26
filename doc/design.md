# `autonameow` design document

```
Copyright(c)2016 Jonas Sjoberg
                 https://github.com/jonasjberg
                 jomeganas@gmail.com

Please see "LICENSE.md" for licensing details.
```

--------------------------------------------------------------------------------


Basic program functionality
===========================
`autonameow` does automatic renaming of files.

The primary goal is to reduce the overhead and manual work required to
apply a strict file naming convention uniformly and consistently.
convention by  needed is to find suitable file names from a set of rules.

The user specifies the target file name structure, defined as a number of
ordered fields, in a configuration file.

The program is to fill out these fields by first reading in a bunch of data
from and about the file, which is then analyzed and ranked by probability, as
defined by some set of rules.

#### Example:

Name template: `[timestamp] [title] -- [author].[ext]`

Resulting file name: `1998-04-01 Report of the IAB Security Architecture Workshop -- Bellovin. S.txt`


High-level logic
----------------
Breakdown of what needs to happen to automatically rename a file:

#### 1. Collect information:

* From file **name**
    * `seemingly giant cat in dollhouse.jpg`
    * Try to extract date/time-information, title, keywords, etc.

* From file **contents**
    * Get plain text from the file contents.
    * Extraction technique would be specfic to file type;
        * Run `OCR` on images to extract textual content.
        * Convert pdf documents to plain text.
        * Do conversion specific to file (magic) type.

* From file **metadata**
    * Extract information from embedded metadata.
    * Metadata type and extraction technique is specfic to file type;
      "media" often have `Exif` data, pdf documents, etc.

* From file **surroundings** (optional)
    * Extract information from the surrounding structure;
        * Parent directory name
        * Other files in the directory


#### 2. Evaluate any results.

* Sort
    * Prioritize items by weights and/or fixed rules.
    * For example, the EXIF-tag `Date/Time Original` would be selected
      before `Modify Date`. Maybe not always though.

* Filter
    * Remove and/or mark:
        * Obviously incorrect entries.
        * Unplausible entries.
        * Entries matching some kind of ruleset or blacklist.
    * Apply user-specified filters
        * Specified in configuration file
        * Specified as command line options at program invocation


#### 3. Construct a new file name from the data.

* Fill fields in file name template with most probable values.


#### 4. Rename the file.

* (Ask user to proceed (?))
* Do belt+suspenders sanity checks to make sure;
    * File still exists, is readable, etc..
    * Destination won't be clobbered, is writable, etc..
* Rename file to the generated file name.


Example
-------

#### 1. Collect information:
Reading from file `~/Downloads/DSCN9659.jpg`

* From file **name**
    * `DSCN9659.jpg` --- No obvious information in file name.
        * Scans using progressively liberal/tolerant matching, I.E. where
          the search "fuzzyness" increases progressively if no results are
          found, could return a lot of garbage in such cases.

        * **TODO:** Figure out how to handle this. Test file name length,
          number of letters, digits, etc and decide which scans to run based
          on results?

* From file **contents**
    * Run `OCR` on image to extract textual content.
        * Check if any textual content is returned, run text-scans if true.

* From file **metadata**
    * Extract image `Exif` information with `PIL`.
        * Get date/time-information from `Exif` data.
        * Get tags/keywords/etc from `Exif` data.

* From file **surroundings** (optional)

    **TODO:** Figure out how to handle this. See for example how `beets`
    handles jobs/tasks.



Naming convention
================================================================================

The naming convention is a configurable pattern of fields that is used for
constructing new file names.

File type determines which naming pattern is used.
Different naming patterns apply to different file types, should be
user configurable.

In the examples below, ' _ ' is a customizable field separator.



The terms used in the examples are defined as follows:

| **Term** | **Field description**       | **Example**  |
|----------|-----------------------------|--------------|
| ` _ `    | (top-level) field separator | `_`,` `,`-`  |
| `[date]` | ISO-8601 style date         | `2016-02-29` |
| `[time]` | ISO-8601 style time         | `13-24-34`   |
| `[ext]`  | file extension              | `jpg`,`txt`  |


<!-- The markdown previewer in PyCharm can't handle this ..    -->
<!-- +----------+-----------------------------+--------------+ -->
<!-- | **Term** | **Field description**       | **Example**  | -->
<!-- +==========+=============================+==============+ -->
<!-- | ` _ `    | (top-level) field separator | `_`,` `,`-`  | -->
<!-- | `[date]` | ISO-8601 style date         | `2016-02-29` | -->
<!-- | `[time]` | ISO-8601 style time         | `13-24-34`   | -->
<!-- | `[ext]`  | file extension              | `jpg`,`txt`  | -->
<!-- +----------+-----------------------------+--------------+ -->
<!-- Definition of terms                                       -->



Photos
------
Photo images *(schematics, etc excluded?)* should match the pattern:

    [date] _ [time] _ [description/name] . [ext]
                          (optional)       (jpg)



Pdf books
---------
File names are to match the pattern:

    [title] _ [edition] _ [author(s) last name] _ [publisher] _ [year] . [ext]
              (optional)                                                 (pdf)


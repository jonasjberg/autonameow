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

1. From file **name**

    * `seemingly giant cat in dollhouse.jpg`
    * Try to extract date/time-information, title, keywords, etc.

2. From file **contents**

    * Get plain text from the file contents.
    * Extraction technique would be specfic to file type;
        * Run `OCR` on images to extract textual content.
        * Convert pdf documents to plain text.
        * Do conversion specific to file (magic) type.

3. From file **metadata**

    * Extract information from embedded metadata.
    * Metadata type and extraction technique is specfic to file type;
      "media" often have `Exif` data, pdf documents, etc.

4. From file **surroundings** (optional)

    * Extract information from the surrounding structure;
        * Parent directory name
        * Other files in the directory


#### 2. Evaluate/process any results.

1. Sort

    * Prioritize items by weights and/or fixed rules.
        * For fixed rules, use a configuration file for specifying rules to be
          matched.
            * **Example:** If file (magic) type is image, and the extension is
              upper-case PNG and the file name contains Sreenshot, OCR text
              contains anything instagram-related; THEN run a specific routine
              or apply a certain template.
        * Use weights to indicate probability that some information is correct.
            * **Example:** Exif DateTimeOriginal date/time-information would be
              weighted 1, while date/time-information extracted by
              brute-forcing textual contents would have a weight of 0.1.

    * For example, the EXIF-tag `Date/Time Original` would be selected
      before `Modify Date`. Maybe not always though.

2. Filter

    * Remove and/or mark:
        * Obviously incorrect entries.
        * Unplausible entries.
        * Entries matching some kind of ruleset or blacklist.

    * Apply user-specified filters
        * Specified in configuration file
        * Specified as command line options at program invocation


#### 3. Perform actions

1. Fill fields in file name template with most probable values.

    * Construct a new file name from the data.

2. Rename the file.

    * Do belt+suspenders sanity checks to make sure;
        * File still exists, is readable, etc..
        * Destination won't be clobbered, is writable, etc..
        * (Ask user to proceed (?))

    * Rename file to the generated file name.

3. Display results

    * Print summary of results/actions performed/etc.
        * Output is determined by the user.
        * An option like `--dry-run` or similar would skip renaming altogether.


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

| **Term**       | **Field description**           | **Example**           |
|----------------|---------------------------------|-----------------------|
| ` _ `          | (top-level) field separator     | `_`,` `,`-`           |
| `[date]`       | [ISO-8601][2] style date        | `2016-02-29`          |
| `[time]`       | ISO-8601 style time             | `13-24-34`            |
| `[datetime]`   | ISO-8601 date and time          | `2016-02-29_132434`   |
| `[ext]`        | file extension                  | `jpg`,`txt`           |
| `[tags]`       | [filetags][1]                   | `projects`,`dev`      |


<!-- The markdown previewer in PyCharm can't handle this ..    -->
<!-- +--------------+-----------------------------+-----------------------+ -->
<!-- | **Term**     | **Field description**       | **Example**           | -->
<!-- +==============+=============================+=======================+ -->
<!-- | ` _ `        | (top-level) field separator | `_`,` `,`-`           | -->
<!-- | `[date]`     | ISO-8601 style date         | `2016-02-29`          | -->
<!-- | `[time]`     | ISO-8601 style time         | `13-24-34`            | -->
<!-- | `[datetime]` | ISO-8601 date and time      | `2016-02-29_132434`   | -->
<!-- | `[ext]`      | file extension              | `jpg`,`txt`           | -->
<!-- | `[tags]`     | [filetags][1]               | `projects`,`dev`      | -->
<!-- +--------------+-----------------------------+-----------------------+ -->
<!-- Definition of terms                                                    -->

[1]: https://github.com/novoid/filetags
[2]: https://xkcd.com/1179/


Photos
------
Photo images *(schematics, etc excluded?)* should match the pattern:

    [date] _ [time] _ [description/name] -- [tags] . [ext]
                          (optional)                 (jpg)


Pdf books
---------
File names are to match the pattern:

    [title] _ [edition] _ [author(s) last name] _ [publisher] _ [year] . [ext]
              (optional)                                                 (pdf)


Videos
------
Videos  should match the pattern:

    [date] _ [time] _ [description/name] -- [tags] . [ext]




--------------------------------------------------------------------------------


Implementation details
======================


Metadata data structure
-----------------------
The data structure for metadata is still undecided. The following is only a
draft/example and is subject to change.


### Example:

One piece of extracted date/time-information would store:

* The date/time itself as a datetime-object.

* It should probably also keep track of the source -- who found this piece of
  information?

* A "weight" or some kind of metric that approximates how reliable the
  information is, I.E. how probable is it that it is correct?

    * Note that the "correctness" is entirely context-specific; datetime for a
      pdf-document would be correct if it matches the time of the document
      release.

The reason for keeping track of the data source (aside from debugging
information) would be to use later when deciding on what data to use, in other
words, it would serve the same purpose as the "weight".


### Example of possible data structure:
Dictionary with some values being lists of dictionaries.

```python
file_info = { 'title': 'The Cats Mjaowuw',
              'author': 'Gibson',
              'publisher': None,
              'edition': None,
              'dateandtime': [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                                 'source': pdf_metadata,
                                 'comment': "Create date",
                                 'weight': 1 },
                               { 'datetime': datetime.datetime(2010, 1, 2, 34, ..),
                                 'source': pdf_metadata,
                                 'comment': "Modify date",
                                 'weight': 0.8 } ],
              'description': 'Best-selling Novel',
              'tags': set(['cat', 'best', 'book']) }
```


Analyzer return values
----------------------


file_object
filters

	AbstractAnalyzer

		get_datetime()
		get_title()
		get_author()


    FilesystemAnalyzer

		get_datetime()
                        <-- dict -- _get_datetime_from_filesystem()
                        <-- dict -- _get_datetime_from_name()

		get_title()
		get_author()


    ImageAnalyzer

		get_datetime()
                        <-- dict -- _get_exif_datetime()
                        <-- dict -- _get_ocr_datetime()

		get_title()
		get_author()

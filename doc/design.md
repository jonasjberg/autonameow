`autonameow` -- Design Document
================================================================================


1. Read data from file:
    * File name
    * Contents
    * Metadata
2. Evaluate the results.
    * Sort
    * Filter
3. Construct a new file name from the data.
4. Rename the file.




Naming convention
================================================================================

The naming convention is a configurable pattern of fields that is used for
constructing new file names.

File type determines which naming pattern is used.
Different naming patterns apply to different file types, should be
user configurable.

In the examples below, ' _ ' is a customizable field separator.



The terms used in the examples are defined as follows.

+----------+-----------------------------+--------------+
| **Term** | **Field description**       | **Example**  |
+==========+=============================+==============+
| ` _ `    | (top-level) field separator | `_`,` `,`-`  |
| `[date]` | ISO-8601 style date         | `2016-02-29` |
| `[time]` | ISO-8601 style time         | `13-24-34`   |
| `[ext]`  | file extension              | `jpg`,`txt`  |
+----------+-----------------------------+--------------+



Definition of terms


Photos
------
Photo images (schematics, etc excluded?) should match the pattern:

    [date] _ [time] _ [description/name] . [ext]
                          (optional)       (jpg)



Pdf books
---------
File names are to match the pattern:

    [title] _ [edition] _ [author(s) last name] _ [publisher] _ [year] . [ext]
              (optional)                                                 (jpg)


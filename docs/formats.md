`autonameow` data formats
=========================

```
Copyright(c)2016-2017 Jonas Sjoberg
                      https://github.com/jonasjberg
                      jomeganas@gmail.com

Please see "LICENSE.txt" for licensing details.
```

--------------------------------------------------------------------------------


Current Formats
---------------
The following formats will/should/have be/been fully/partially reworked:

- Results returned by analyzers, gathered by `Analysis`
- All analyzer results, stored in `Analysis.results`
- Configuration file


### Configuration File
This is the current format of the configuration file.
Note that the format is still under heavy development and will most likely be
changed. Manual verification of the source code is recommended.


#### Overview
The configuration file should provide means to specify how *actions are
performed* to some subset of *files matching some criteria*.

The configuration file contains a list of __rules__.
Each rule consists of two main parts;

1. `conditions` -- __which files__ that the rule should be applied to
2. `data_sources` -- __what data__ should be used to construct the new name
3. `name_format`/`name_template` -- __format__ of the new file name

In the current state, the only possible *action* is constructing new file names
and optionally also renaming the file to this new file name.

Thus, the configuration specifies how the construction of file names should be
performed.


__In short;__
Files that match the `conditions` of a given rule will be renamed by populating
the naming convention given by `name_format` with the information given by
sources specified in `data_sources`.


#### Conditions
The testing of the specified conditions depends on the value of `_exact_match`.

* If `_exact_match` is __`True`__; all specified conditions must be met for the
  rule to apply to the given file.

* If `_exact_match` is __`False`__; then the rule with the highest number of
  satisfied conditions is chosen to apply to the given file.
    * In the case where multiple rules end up tied for the highest count of
      satisfied conditions, the `_weight` field is used to sort the tied rules
      in order to pick out a single rule that applies to the file.
<!-- NOTE: What happens if this still fails to produce a single "winner"? -->


This is the internal data structure for the conditions of a single rule;

```python
'conditions': {
    'filesystem': {
        'pathname': None,
        'basename': None,
        'extension': None
    },
    'contents': {
        'mime_type': None
    }
},
```

Entries with missing values are considered equal to entries with value `None`.

Here is an example of the first section; `filesystem`:

```python
'filesystem': {
    'pathname': '(~/temp|/tmp)',
    'basename': '^\..*',
    'extension': None
},
```

These fields support regular expressions. This is implemented using the Python
`re` module from the standard library.

This example should match hidden files (basename starts with a period) located
in either `~/temp` or `/tmp` with any file extension.



The second section, `contents`; contain tests on the file contents.

```python
'contents': {
    'mime_type': 'image/jpeg'
}
```

This example would match jpeg image files.


#### Data Sources
Next is the second main part of each rule; `data_sources`.

Each field corresponds to a field in `name_template`.  The field values specify
*which data* should be used to populate that field.

```python
'DATA_SOURCES': {
    'datetime': None,
    'description': None,
    'title': None,
    'author': None,
    'publisher': None,
    'extension': 'filename.extension',
    'tags': None
}
```

The following example is part of a rule that applies to `MOBI` e-books:


```python
'data_sources': {
    'datetime': 'metadata.exiftool.XMP-dc:PublicationDate',
    'description': ['metadata.exiftool.XMP-dc:Description',
                    'metadata.exiftool.XMP-dc:Subject'],
    'title': ['metadata.exiftool.XMP-dc:Title',
              'metadata.exiftool.XMP-dc:UpdatedTitle'],
    'author': 'metadata.exiftool.XMP-dc:Creator',
    'publisher': 'metadata.exiftool.XMP-dc:Publisher',
    'extension': 'filename.extension',
    'tags': None
}
```

The field value format is nested, with periods separating the parts.
There might be multiple sources for `extension` data, for example;

1. Extracted from the original file name:

    ```python
    {
        'extension': 'filesystem.basename.extension'
    }
    ```

2. Extracted from the file MIME type:

    ```python
    {
        'extension': 'contents.mime_type.extension'
    }
    ```

<!-- NOTE: Field format is still not implemented and very likely to change! -->


#### Default Configuration File
This is the default configuration file in the most basic internal format;
nested structure of dictionaries and lists.

```python
DEFAULT_CONFIG = {

    #   File Rules
    #   ----------
    #   File rules determine which files are handled and how they are handled.
    #
    #   Each rule specifies conditions that should be met for the rule to apply
    #   to a given file.
    #
    #   * If 'exact_match' is True, __all__ conditions must be met,
    #     otherwise the rule is considered to not apply to the given file.
    #
    #   * If 'exact_match' is False, the rule with the highest number of
    #     satisfied conditions is used.
    #     When multiple rules end up tied for the "best fit", I.E. they all
    #     have an equal amount of satisfied conditions; 'weight' is used
    #     to prioritize the candidates.
    #
    'FILE_RULES': [
        {'description': 'test_files Gmail print-to-pdf',
         'exact_match': True,
         'weight': None,
         'NAME_FORMAT': '{datetime} {title}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'basename': 'gmail.pdf',
                 'extension': 'pdf',
             },
             'contents': {
                 'mime_type': 'pdf',
             },
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.PDF:CreateDate',
             'title': 'filesystem.basename.prefix',
             'extension': 'filesystem.basename.extension'
         }
         },
        {'description': 'test_files smulan.jpg',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'basename': 'smulan.jpg',
             },
             'contents': {
                 'mime_type': 'jpg',
             },
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'filesystem.basename.extension'
         }
         },
        {'description': 'Sample Entry for Photos with strict rules',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description} -- {tags}.{extension}',
         'CONDITIONS': {
             'filesystem': {
                 'pathname': '~/Pictures/incoming',
                 'basename': 'DCIM*',
                 'extension': 'jpg',
                 'date_accessed': None,
                 'date_created': None,
                 'date_modified': None
             },
             'contents': {
                 'mime_type': 'jpg',
             },
             'metadata': {
                 'exif': {
                     # NOTE: Possibly use exiftool for all metadata?
                     # http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
                     'datetimeoriginal': None,
                     'camera-model': None
                 },
             }
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.EXIF:DateTimeOriginal',
                          'metadata.exiftool.EXIF:DateTimeDigitized',
                          'metadata.exiftool.EXIF:CreateDate'],
             'description': 'plugin.microsoft_vision.caption',
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filesystem.basename.extension',
             'tags': 'plugin.microsoft_vision.tags'
         }
         },
        {'description': 'Sample Entry for EPUB e-books',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': 'default_book',
         'CONDITIONS': {
             'filesystem': {
                 'pathname': None,
                 'basename': None,
                 'extension': 'epub'
             },
             'contents': {
                 'mime_type': 'application/epub+zip',
                 'metadata': 'metadata.XMP-dc.***'
             }
         },
         'DATA_SOURCES': {
             'datetime': ['metadata.exiftool.XMP-dc:PublicationDate',
                          'metadata.exiftool.XMP-dc:Date'],
             'description': None,
             'title': 'metadata.exiftool.XMP-dc:Title',
             'author': ['metadata.exiftool.XMP-dc:Creator',
                        'metadata.exiftool.XMP-dc:CreatorFile-as'],
             'publisher': 'metadata.exiftool.XMP-dc:Publisher',
             'edition': None,
             'extension': 'filesystem.basename.extension',
             'tags': None
         }
         },
    ],

    #  File Name Templates
    #  -------------------
    #  These file name templates can be reused by multiple file rules.
    #  Simply add the template name to the file rule 'NAME_FORMAT' field.
    #
    #  NOTE: If a rule specifies both 'NAME_FORMAT' and 'NAME_TEMPLATE',
    #        'NAME_FORMAT' will be prioritized.
    #
    'NAME_TEMPLATES': {
        'default_document': '{title} - {author} {datetime}.{extension}',
        'default_book': '{publisher} {title} {edition} - {author} {date}.{extension}',
        'default_photo': '{datetime} {description} -- {tags}.{extension}'
    },

    #  File Name Date and Time Format
    #  ------------------------------
    #  Specifies the format of date and time in constructed file names.
    #  Fields are parsed with "datetime" from the Python standard library.
    #  Refer to the "datetime" library documentation for more information;
    #
    #      docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #
    'DATETIME_FORMAT': {
        'date': '%Y-%m-%d',
        'time': '%H-%M-%S',
        'datetime': '%Y-%m-%dT%H%M%S'
    },

    #  Filetags Options
    #  ----------------
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    }
}
```


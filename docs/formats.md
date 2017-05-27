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
    'filename': {
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

Here is an example of the first section; `filename`:

```python
'filename': {
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
'data_sources': {
    'datetime': None,
    'description': None,
    'title': None,
    'author': None,
    'publisher': None,
    'extension': 'filename.extension'
}
```

The following example is part of a rule that applies to `MOBI` e-books:


```python
'data_sources': {
    'datetime': ['metadata.MOBI.PublishDate'],
    'description': ['metadata.MOBI.Description',
                    'metadata.MOBI.Subject'],
    'title': ['metadata.MOBI.BookName',
              'metadata.MOBI.UpdatedTitle'],
    'author': 'metadata.MOBI.Author',
    'publisher': 'metadata.MOBI.Publisher',
    'extension': 'filename.extension',
    'tags': None
}
```

The field value format is nested, with periods separating the parts.
There might be multiple sources for `extension` data, for example;

1. Extracted from the original file name:

    ```python
    {
        'extension': 'filename.extension'
    }
    ```

2. Extracted from the file MIME type:

    ```python
    {
        'extension': 'contents.mime.extension'
    }
    ```

<!-- NOTE: Field format is still not implemented and very likely to change! -->


#### Default Configuration File
This is the default configuration file in the most basic internal format;
nested structure of dictionaries and lists.

```python
DEFAULT_CONFIG = {
    # File rules specify conditions that should be true for the rule to apply
    # for a given file.
    #
    # If '_exact_match' is True, *all* conditions must apply for the rule to be
    # considered a match for a given file.
    # Otherwise, when '_exact_match' is False, the rule with the most amount of
    # satisfied conditions is chosen.
    # If multiple rules end up tied (same amount of satisified conditions for a
    # given file) the '_weight' is used as a last resort to pick out a single
    # rule to use.
    'file_rules': [
        {'_description': 'First Entry in the Default Configuration',
         '_exact_match': False,
         '_weight': None,
         'name_template': 'default_template_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': None
             },
             'contents': {
                 'mime_type': None
             }
         },
         'data_sources': {
             'datetime': None,
             'description': None,
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension'
         }
         },
        {'_description': 'Sample Entry for Photos with strict rules',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '%(datetime(%Y-%m-%dT%H%M%S))s %(description)s -- %(tags)s.%(extension)s',
         'conditions': {
             'filename': {
                 'pathname': '~/Pictures/incoming',
                 'basename': 'DCIM*',
                 'extension': 'jpg'
             },
             'contents': {
                 'mime_type': 'image/jpeg',
                 'metadata': 'exif.datetimeoriginal'
             }
         },
         'data_sources': {
             'datetime': ['metadata.exif.datetimeoriginal',
                          'metadata.exif.datetimedigitized',
                          'metadata.exif.createdate'],
             'description': 'plugin.microsoftvision.caption',
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension',
             'tags': 'plugin.microsoftvision.tags'
         }
         },
        {'_description': 'Sample Entry for EPUB e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '',
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': 'epub'
             },
             'contents': {
                 'mime_type': 'application/epub+zip',
                 'metadata': 'metadata.XMP-dc.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.XMP-dc.PublicationDate',
                          'metadata.XMP-dc.Date'],
             'description': None,
             'title': 'metadata.XMP-dc.Title',
             'author': ['metadata.XMP-dc.Creator',
                        'metadata.XMP-dc.CreatorFile-as'],
             'publisher': 'metadata.XMP-dc.Publisher',
             'edition': None,
             'extension': 'filename.extension',
             'tags': None
         }
         },
        {'_description': 'Sample Entry for MOBI e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': None,
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': ['mobi']
             },
             'contents': {
                 'mime_type': 'application/x-mobipocket-ebook',
                 'metadata': 'metadata.MOBI.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.MOBI.PublishDate'],
             'description': ['metadata.MOBI.Description',
                             'metadata.MOBI.Subject'],
             'title': ['metadata.MOBI.BookName',
                       'metadata.MOBI.UpdatedTitle'],
             'author': 'metadata.MOBI.Author',
             'publisher': 'metadata.MOBI.Publisher',
             'extension': 'filename.extension',
             'tags': None
         }
         }
    ],
    # Templates used when constructing new file names.
    # Can be reused by multiple file rules. Reference the template name
    # in the file rule 'name_template' field.
    'name_templates': [
        {'_description': 'First name template in the Default Configuration',
         '_name': 'default_template_name',
         'name_format': '%(title)s - %(author)s %(datetime)s.%(extension)s'},
        {'_description': 'Ebook name template in the Default Configuration',
         '_name': 'default_ebook_name',
         'name_format': '%(publisher)s %(title)s %(edition)s - %(author)s %(year)s.%(extension)s'}
    ]
}
```


Legacy Formats
--------------
These are the data structures/formats used as of autonameow version v0.3.0.

### Configuration File
Legacy format of the configuration file rules, `core.config_defaults.rules`.

```python
rules = {'record_my_desktop': {'type': ['ogv', 'ogg'],
                               'name': None,
                               'path': None,
                               'prefer_datetime': 'accessed',
                               'prefer_title': None,
                               'new_name_template': DEFAULT_NAME,
                               'tags': []},
         'photo_android_msg': {'type': 'jpg',
                               'name': r'^received_\d{15,17}\.jpeg$',
                               'path': None,
                               'prefer_datetime': 'android_messenger',
                               'prefer_title': None,
                               'new_name_template': DEFAULT_NAME,
                               'tags': []},
         'screencapture': {'type': 'png',
                           'name': r'^screencapture.*.png$',
                           'path': None,
                           'prefer_datetime': 'screencapture_unixtime',
                           'prefer_title': None,
                           'new_name_template': DEFAULT_NAME,
                           'tags': ['screenshot']},
         'document_default': {'type': 'pdf',
                              'name': None,
                              'path': None,
                              'prefer_author': 'PDF:Author',
                              'prefer_datetime': 'CreationDate',
                              'prefer_title': None,
                              'prefer_publisher': 'PDF:EBX_PUBLISHER',
                              'new_name_template': DOCUMENT_NAME,
                              'tags': []},
         'ebook_pdf': {'type': 'pdf',
                       'name': None,
                       'path': None,
                       'prefer_author': 'PDF:Author',
                       'prefer_datetime': 'CreationDate',
                       'prefer_title': 'PDF:Title',
                       'prefer_publisher': 'PDF:EBX_PUBLISHER',
                       'new_name_template': EBOOK_NAME,
                       'tags': []},
         }
```

### Analysis Results
Current format of the analysis results data structure,
`core.analyze.analysis.Analysis.results`.

autonameow executed with the command;
```bash
/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6 /Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/autonameow/__main__.py --debug --list-all -- /Users/jonas/Dropbox/LNU/1DV430_IndividuelltProjekt/src/js224eh-project.git/test_files/2010-01-31_161251.jpg
```

Produced results:

```python
results = {
        "datetime": {
                "ImageAnalyzer": [
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetimeoriginal",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetimedigitized",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "datetime",
                                "weight": 0.75
                        }
                ],
                "FilesystemAnalyzer": [
                        {
                                "value": "datetime.datetime(2016, 2, 24, 15, 8, 34)",
                                "source": "modified",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2017, 5, 1, 16, 12, 40)",
                                "source": "created",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2017, 5, 5, 0, 1, 50)",
                                "source": "accessed",
                                "weight": 0.25
                        }
                ],
                "FilenameAnalyzer": [
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "very_special_case",
                                "weight": 1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 0, 0)",
                                "source": "regex_search",
                                "weight": 0.25
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 16, 12, 51)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 31, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 1, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        },
                        {
                                "value": "datetime.datetime(2010, 1, 1, 0, 0)",
                                "source": "bruteforce_search",
                                "weight": 0.1
                        }
                ]
        },
        "publisher": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": null
        },
        "title": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": []
        },
        "tags": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": []
        },
        "author": {
                "ImageAnalyzer": null,
                "FilesystemAnalyzer": null,
                "FilenameAnalyzer": null
        }
}
```


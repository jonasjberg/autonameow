`autonameow` data formats
=========================

```
Copyright(c)2016-2017 Jonas Sjoberg
                      https://github.com/jonasjberg
                      jomeganas@gmail.com

Please see "LICENSE.txt" for licensing details.
```

--------------------------------------------------------------------------------


Configuration File
==================

Current Formats
---------------
This is the current format of the configuration file.
Note that the format is still under heavy development and will most likely be
changed. Manual verification of the source code is recommended.


### Overview
The configuration file should provide means to specify how *actions are
performed* to some subset of *files matching some criteria*.

The configuration file contains a list of __rules__.
Each rule consists of two main parts;

1. `conditions` -- statements that are evaluated to determine __which files__
   that the rule applies to
2. `data_sources` -- determine __what data__ should be used to construct the
   new name. Specifies sources for each of the name template placeholder fields
3. `name_format`/`name_template` -- __format__ of the new file name, uses
   constants and special "placeholder fields" to be populated

In the current state, the only possible *action* is constructing new file names
and optionally also renaming the file to this new file name.

Thus, the configuration specifies how the construction of file names should be
performed and which format to use for the final file; only for the files that
match some criteria, I.E. conditions evaluate true.


__In short;__
Files that match the `conditions` of a given rule will be renamed by populating
the naming convention given by `name_format` with the information given by
sources specified in `data_sources`.

#### Internals
Each rule is represented as an instance of the `FileRule` class. These are
instantiated when the `Configuration` class instance is created; which happens
each time the program is executed, before files are processed.


### Conditions
The testing of the specified conditions depends on the value of `_exact_match`.

* If `_exact_match` is __`True`__; all specified conditions must be met for the
  rule to apply to the given file.

* If `_exact_match` is __`False`__; then the rule with the highest number of
  satisfied conditions is chosen to apply to the given file.
    * In the case where multiple rules end up tied for the highest count of
      satisfied conditions, the `_weight` field is used to sort the tied rules
      in order to pick out a single rule that applies to the file.
<!-- NOTE: What happens if this still fails to produce a single "winner"? -->

This is an example of conditions from a single rule in the default configuration;

```python
'CONDITIONS': {
    'filesystem.pathname.full': None,
    'filesystem.basename.full': None,
    'filesystem.basename.extension': None,
    'contents.mime_type': None
},
```

Entries with missing values are considered equal to entries with value `None`
and are skipped.


The first three conditions has to do with the file name;

```python
'CONDITIONS': {
    'filesystem.pathname.full': '(~/temp|/tmp)',
    'filesystem.basename.full': '^\..*',
    'filesystem.basename.extension': None
},
```

These fields support regular expressions. This is implemented using the Python
`re` module from the standard library.

This example should match hidden files (basename starts with a period) located
in either `~/temp` or `/tmp` with any file extension.


The last condition tests the file MIME type.

```python
'CONDITIONS': {
    'contents.mime_type': 'image/*'
}
```

This example would match any kind of image file.


#### Internals
Each `FileRule` instance stores a list of conditions that are evaluated by a
`RuleMatcher`. The conditions are encapsulated in instances of the
`RuleCondition` class.

The `RuleCondition` class validates the condition at instantiation. It also
stores a reference to a `FieldParser` class that is suited to evaluate the
condition.



### Data Sources
Next is the second main part of each rule; `DATA_SOURCES`.

Each field corresponds to a "placeholder field" in `name_template`.
The field values specify *which data* should be used to populate that field.

```python
'DATA_SOURCES': {
    'datetime': metadata.exiftool.PDF:CreateDate,
    'description': None,
    'title': metadata.exiftool.XMP-dc:Title,
    'author': metadata.exiftool.XMP-dc:Creator,
    'publisher': metadata.exiftool.XMP-dc:Publisher,
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


Default Configuration File
--------------------------
This is the default configuration file in the internal dict format as of
version `v0.4.3`.

```python
DEFAULT_CONFIG = {

    #   File Rules
    #   ==========
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
         'NAME_FORMAT': '{datetime} {title}.{extension}',
         'CONDITIONS': {
             'filesystem.basename.full': 'gmail.pdf',
             'filesystem.basename.extension': 'pdf',
             'contents.mime_type': 'application/pdf',
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.PDF:CreateDate',
             'title': 'filesystem.basename.prefix',
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'test_files smulan.jpg',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description}.{extension}',
         'CONDITIONS': {
             'filesystem.basename.full': 'smulan.jpg',
             'contents.mime_type': 'image/jpeg',
         },
         'DATA_SOURCES': {
             'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
             'description': 'plugin.microsoft_vision.caption',
             'extension': 'filesystem.basename.extension'
         }
         },
        # ____________________________________________________________________
        {'description': 'Sample Entry for Photos with strict rules',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': '{datetime} {description} -- {tags}.{extension}',
         'CONDITIONS': {
             'filesystem.pathname.full': '~/Pictures/incoming',
             'filesystem.basename.full': 'DCIM*',
             'filesystem.basename.extension': 'jpg',
             'contents.mime_type': 'image/jpeg',
             'metadata.exiftool.EXIF:DateTimeOriginal': 'Defined',
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
        # ____________________________________________________________________
        {'description': 'Sample Entry for EPUB e-books',
         'exact_match': True,
         'weight': 1,
         'NAME_FORMAT': 'default_book',
         'CONDITIONS': {
             'filesystem.pathname.full': '.*',
             'filesystem.basename.full': '.*',
             'filesystem.basename.extension': 'epub',
             'contents.mime_type': 'application/epub+zip',
             'metadata.exiftool.XMP-dc:Creator': 'Defined',
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
    #  ===================
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
    #  ==============================
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
    #  ================
    #  Options for functionality related to the "filetags" workflow.
    #
    'FILETAGS_OPTIONS': {
        'filename_tag_separator': ' -- ',
        'between_tag_separator': ' '
    },

    'autonameow_version': constants.PROGRAM_VERSION
}
```



Internal Data Structures
========================

Extracted Data
--------------

### Nested Structure (dict)

* `filesystem`
    * `basename`
        * `full`
        * `prefix`
        * `suffix`
        * `extension`
    * `pathname`
        * `full`
        * `parent`
    * `date_accessed`
    * `date_created`
    * `date_modified`
* `contents`
    * `mime_type`
    * `textual`
        * `raw_text`
        * `paginated`
        * `number_pages`
    * visual
        * `ocr_text`
        * `ocr_description`
        * `ocr_tags`
    * binary
        * `placeholder_field`
* `metadata`
    * `exiftool`
    * `pypdf`
* `plugin`
    * `microsoft_vision`
    * `guessit`


### Query Strings
Extractor query strings as of version `v0.4.2`.

* `contents.textual.raw_text`
* `contents.textual.encrypted`
* `contents.textual.number_pages`
* `contents.textual.paginated`
* `contents.visual.ocr_text`
* `filesystem.basename.extension`
* `filesystem.basename.full`
* `filesystem.basename.prefix`
* `filesystem.basename.suffix`
* `filesystem.pathname.full`
* `filesystem.pathname.parent`
* `metadata.exiftool.[exiftool_fields]`
* `metadata.pypdf.[PyPDF2_fields]`
* `metadata.pypdf.number_pages`
* `metadata.pypdf.paginated`

Search the source code for currently used extractor query strings:

```bash
grep --color=always --exclude-dir={.git,.idea} --include="*.py" -rnHa -- data_query_string . | tr -s ' '
```


Alternative Layout
------------------

* Contents
    * Text
        * `pages` (list of pages)
            * ( Page 1 )
                * `page_number`
                * `contents` (list of text lines)
            * ( Page n )
                * `page_number`
                * `contents` (list of text lines)
        * Number of pages
        * EXIF Metadata
    * Image
        * Text
            * `contents` (list of text lines)
        * EXIF metadata
    * Video
        * ..
        * ..


Rule Configuration File Syntax
==============================

```
- ExactMatch: True
- Weight: 0.2
- Filename
    - Pathname: "~/today"
    - Basename: "*screenshot*"
    - Extension: *.png"
- Contents
    - Mime type: "image/png"
```

###

| Description               | Current Pathname        | Current Basename             | Extension | Contents |
|---------------------------|-------------------------|------------------------------|-----------|----------|
| Websites printed to html  | `~/Dropbox/incoming`    | `[URL] [YYYY-MM-DD] [title]` | `pdf`     | First line of all pages matches: `4/29/2017 [title]` |



### Websites saved to PDF from browsers "Print to PDF..":

* Pathname: `~/Dropbox/incoming`
* Current Basename: `[URL] [YYYY-MM-DD] [title]`
* Extension: `pdf`
* Contents:
    * First line of all pages match: `4/29/2017 [\W+] [title]`
    * Last line of all pages match: `[URL] [current_page_number]/[number_pages]`

`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


Ideas and Notes
===============
Various ideas and possible features.


Field Candidates
----------------
For cases where placeholder field data should be extracted from a document
text, the user should be able to control what content should be used.

For the placeholder field `title` for instance, the user might want to specify
a number of possible candidates. This would be done per file rule.
The candidates could be expressed as regular expressions or some other kind of
expression that would be evaluated against textual content extracted from
files.

* Control of data sources possible as of autonameow version `v0.4.4`:

    ```python
    'DATA_SOURCES': {
        'datetime': metadata.exiftool.PDF:CreateDate,
        'title': metadata.exiftool.XMP-dc:Title,
    }
    ```

* Possible redesigned configuration of data sources:

    ```python
    'DATA_SOURCES': {
        'datetime': { 
            # List of sources ordered by priority.
            'source': [metadata.exiftool.PDF:CreateDate,
                       metadata.exiftool.PDF:ModifyDate]
        }
        'title': {
            # Contents from source must match one of the regular expressions.
            'source': 'contents.textual.raw_text',
            'candidates': ['The Tale of Tail', 'The .* of .*', '^.* Tale .*$']
        }
    }
    ```

* Another possible variant of specifying sources:

```python
'DATA_SOURCES': {
    'datetime': { 
        # List of sources ordered by priority.
        'source': [metadata.exiftool.PDF:CreateDate,
                   metadata.exiftool.PDF:ModifyDate]
    }
    'title': [
        # Raw text source is evaluated against two possible candidates.
        # If any expression evaluates true, "override" is used as the title.
        { 'source': 'contents.textual.raw_text',
          'candidates': [
            { 'expression': ['The Tale of Tail', 'The .* of .*', '^.* Tale .*$'],
              'override': 'The Tale of Tail' },
            { 'expression': ['Catriarchy', 'Tuna Activism'],
              'override': 'Gibson is Lord' }
          ]
        },
        # If the file basename (without extension) matches any of the two
        # expressions, "The Tale of Tail" is used as the title.
        { 'source': 'filesystem.basename.prefix',
          'candidates': [
            { 'expression': ['The-Tale-of-Tail', 'The-Tale-.*'],
              'override': 'The Tale of Tail' },
          ]
        }
    ]
    'author': metadata.exiftool.XMP-dc:Creator,
    'publisher': metadata.exiftool.XMP-dc:Publisher,
    'extension': 'filename.extension',
    'tags': None
}
```


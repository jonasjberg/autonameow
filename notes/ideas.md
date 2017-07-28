`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


Ideas and Notes
===============
Various ideas on possible upcoming features and changes to `autonameow`.


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
    }
    ```

    Here, the source specification of the `datetime` field is a simple list of
    two sources without any additional qualifier or expression.

    The `title` field can use any of two possible sources; the first source is
    the raw document text, that must match any of the given regular
    expressions.
    The second is the file basename without extension, that also must match one
    two expressions. In the case of a match, a hardcoded "`override`" is used
    as for the `title` field.

* Yet another way of configuring sources:

    ```python
    'DATA_SOURCES': {
        'title': {
            # Text from any of these two sources is to be considered.
            'source': [contents.textual.raw_text,
                       contents.textual.ocr_text],
            # Text from sources is searched for "match" and if found,
            # the text at "replace" is used for the title.
            'candidates': [
                {'match': 'The .* of .*',
                 'replace': 'The Tale of Tail'},
                {'match': '^Regex for Kittens ([1-9]+(st|nd|rd|th) [eE]dition)?$',
                 'replace': 'Regular Expressions for Kittens'}
            ]
        }
    }
    ```

    This way separates the sources from the candidates. The expressions in
    `match` could also be given as a list of expressions.

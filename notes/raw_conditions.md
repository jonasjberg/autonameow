2017-07-07
----------
The "raw" file rule conditions from YAML configuration should be validated.


Examples:

```python
raw_conditions = { 
    'contents.mime_type' = 'application/pdf'
    'filesystem.basename' = 'gmail.pdf'
    'filesystem.extension' = 'pdf'
}
```

```python
raw_conditions = { 
    'contents.mime_type' = 'image/jpeg'
    'filesystem.basename' = 'DCIM*'
    'filesystem.extension' = 'jpg'
    'filesystem.pathname' = '~/Pictures/incoming'
    'metadata.exiftool.EXIF:DateTimeOriginal' = 'Defined'
}
```

```python
raw_conditions = { 
    'contents.mime_type' = 'application/epub+zip'
    'filesystem.basename' = '.*'
    'filesystem.extension' = 'epub'
    'filesystem.pathname' = '.*'
    'metadata.exiftool.XMP-dc:Creator' = 'Defined'
}
```

Possible solutions:

1. Encapsulate each condition in a class instance
    * The class could validate the data at instantiation.
    * The condition field ("query string") `contents.mime_type` is to be
      validated by the `MimeTypeConfigFieldParser`, while the
      `filesystem.basename` condition should be checked by the
      `RegexConfigFieldParser`.


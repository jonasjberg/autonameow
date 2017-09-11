Notes on "MeowURIs"
===================
Jonas Sjöberg, 2017-09-09.

Data is stored in the `Repository` data store, identified by a
`FileObject` and a "MeowURI".


Simplified example of data storage:
```python
file_object = FileObject('/tmp/foo/bar.txt')
data = file_object.abspath
Repository.store(file_object, 'filesystem.pathname.full', data) 
```

The data can then be retrieved by querying the repository:
```python
data = Repository.query(file_object, 'filesystem.pathname.full')
```


The "MeowURI" identifiers are currently, as of 2017-09-09 (commit
b402ae3211fec7f4b5bd66eddf0d72d4cfc94c04) arranged as follows:



__Extractors__ store data without any special prefix;

```
filesystem.basename.full
filesystem.contents.mime_type
metadata.exiftool.EXIF:DateTimeOriginal
metadata.exiftool.QuickTime:CreationDate
metadata.exiftool.XMP-dc:Creator
```


__Analyzers__ store data with the prefix `analysis`;

```
analysis.filetags.datetime
analysis.filetags.description
analysis.filetags.tags
analysis.ebook.author
analysis.ebook.title
analysis.ebook.publisher
```


__Plugins__ store data with the prefix `plugin`;

```
plugin.microsoft_vision.caption
plugin.microsoft_vision.tags
plugin.guessit.date
plugin.guessit.title
```


The "MeowURI" naming convention has been changed a lot and should be cleaned up.
Maybe it would be helpful to add a prefix to the extractor URIs.


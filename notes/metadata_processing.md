`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Metadata Processing
===================
Notes on metadata/field/record processing, normalization, de-duplication, etc.

#### Revisions
* 2017-11-22 --- `jonasjberg` Initial



Data Model
----------
Notes on the underlying data model for information gathered by the providers.

#### Nomenclature

* __fields__ refers to for instance *author*, *title*, etc.
* __record__ refers to a collection of fields, for instance ISBN metadata.

### TODO
I'm still not sure how to model/describe fields with multiple values..

Maybe:
```python
metadata = {
    'title': ['First Title', 'Second Title']
}
```

Or maybe:
```python
metadata = {
    'title_1': ['First Title'],
    'title_2': ['Second Title']
}
```

How would this map to the existing coercer classes and how providers
declare certain data as "multivalued" in the `metainfo`?



Metadata Deduplication
----------------------
Random notes on system for metadata comparison and de-duplication.

### TODO
Likely needed functionality:

* Field Normalization
    * Field-specific transformations.
    * Convert to a "canonical" form, suitable for comparison, etc.
* Field Comparators
    * Compare similarity and equality of values.
    * `'Gibson C. Sjöberg' == 'Sjöberg G.C.' == 'Gibson Cat Sjöberg'`


* Bundle multiple related __fields__ into a "__record__"?
    * Benefits of handling __groups of related fields__?
        * Prioritization of field candidates could first act on a group of
          fields, given a valid ISBN that returns fully populated metadata that
          in turn passes some simple validation, could be passed on as a highly
          *weighted* bundle.
    * What to bundle?
        * Fields associated to a common unique identifier (ISBN, etc.)
        * Originated from the same source or possible "provider"?
        * Bundle results from `exiftool` by `XMP:*`, `EXIF:*`, ..?



Field Normalization
-------------------

<!-- TODO: ... -->



Field Comparison
----------------

<!-- TODO: ... -->

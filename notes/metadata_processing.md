`autonameow`
============
*Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

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


Going with `Records` and `Fields`
---------------------------------
Proceeding under the assumption that the data model is based on
two new classes; `Records` and `Fields` ..

### Problems hopefully solved by `Records`
Some records are more likely to be correct;

* Increase weight of records that contain a unique identifier.
* Weight by number of fields.
* Use field-specific weights from contained fields.

```python
r1 = Record(author='Gibson', title='Meow', identifier=ISBN('123456789'))
r2 = Record(author='Gibson', title='Meow')
r3 = Record(author='G.', title='Meow')
assert r1.weight > r2.weight > r3.weight
```


### Problems hopefully solved by `Fields`

* Comparison/similarity-tests

```python
f1 = Author('Gibson Sjöberg')
f2 = Author('gibson sjöberg')
f3 = Author('G.S.')
f4 = Author('G')
assert f1 == f2
assert f1 != f3
assert f1 != f4
assert f1.weight == f2.weight > f3.weight > f4.weight

# Using 'util.text.similarity.normalized_levenshtein()':
assert similarity(f1, f2) == 0.43   # 'Gibson Sjöberg' -> 'Gibson'
assert similarity(f1, f3) == 0.14   # 'Gibson Sjöberg' -> 'G.S.'
assert similarity(f1, f4) == 0.07   # 'Gibson Sjöberg' -> 'G'
assert similarity(f2, f3) == 0.17   # 'Gibson'         -> 'G.S.'
assert similarity(f2, f4) == 0.17   # 'Gibson'         -> 'G'
assert similarity(f3, f4) == 0.25   # 'G.S.'           -> 'G'
```

### Unique Identifiers and Special Cases
A notable special case when comparing ISBN metadata from a book that specifies
different ISBN-numbers for different "releases", E.G. "e-ISBN", "ISBN", etc.

Example:

```python
eISBN = {
    'title': 'Computational Intelligence Methods And Techniques',
    'authors': ['Leszek Rutkowski'],
    'publisher': 'Springer',
    'year': '2008',
    'language': 'eng',
    'isbn10': '3540762884',
    'isbn13': '9783540762881'
}

ISBN = {
    'title': 'Computational Intelligence: Methods And Techniques',
    'authors': ['Leszek Rutkowski'],
    'publisher': 'Springer',
    'year': '2008',
    'language': 'eng',
    'isbn10': '3540762876',
    'isbn13': '9783540762874'
}
```

For the purposes of finding say a suitable `title`, these two *records* should
probably be considered equivalent..

All fields except the "unique identifiers"; `isbn10`, `isbn13` and the `title`
differ.  Trivial normalization of the titles before comparison probably renders
the `title` fields identical.

The point is that the system must be flexible enough to handle cases like this,
where "unique identifiers" no longer carry the assumed "probabilistic weight".



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

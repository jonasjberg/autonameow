`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

High Level "Change Operations"
==============================
Ideas on a possible new abstract high-level model of assembling a new filename.

#### Revisions
* 2018-11-04 --- `jonasjberg` Initial.


Motivation
----------
The idea is to add a new way of describing and reasoning about the sequence of
very different events involved in coming up with a new filename. Hopefully this
might inspire progress, clean up the codebase and allow plugging in machine
learning techniques later on.


Examples of Current Workings
----------------------------
Comparing two common paths through the program;

1. One based on populating fields in a name template from various data sources,
   often not reusing anything of the original filename.

    ```
    Original filename  : 'MEOW.docx'
    Name Template      : '{date} {title}.{extension}'
    Post-processing    : None
    Resulting filename : '2018-11-04 This is the Meow.pdf'
    ```

2. One where only "post-processing" is performed.

    ```
    Original filename  : 'MEOW.docx'
    Name Template      : N/A
    Post-processing    : Lower-case filename
    Resulting filename : 'meow.docx'
    ```

Note that, in practice, these two are often mixed to various degrees.

3. Both 1 and 2 in sequence

    ```
    Original filename  : 'MEOW.docx'
    Name Template      : '{date} {title}.{extension}'
    Post-processing    : Lower-case filename
    Resulting filename : '2018-11-04 this is the meow.pdf'
    ```

Currently, this is always done in sequence. First check if a name template
should be used, and if this is the case, try to populate it. Then do any
"post-processing" changes.
Quite a few cases don't fit this system, like "tokenizing" and re-using parts
of the original filename as name template field data, or as guiding data for
deciding on what metadata to use for some field. Also "unpacking" metadata
values and dealing with cases like `The Title Second Edition 2E` that are
currently way too difficult to work around.


The New System
--------------
Instead of having the single static linear flow through the process, the new
system would break down every action into atomic changes, similar to how humans
perform renaming tasks manually. Examples follow.

### Example 1
Starting with these filenames;

```
foo_01.txt
foo_02.txt
03_foo.txt
```

We might want to end up with this;

```
foo_01.txt
foo_02.txt
foo_03.txt
```

Which could be described as splitting the filenames into parts using `_` as a
delimiter, followed by shifting the `03` to the left; I.E. `['03', 'foo']`
becomes `['foo', '03']`, which is the joined with `_` which gives the result
`foo_03.txt`.

Should be possible to integrate machine learning techniques with this kind of thing.


### Example 2
Letter case lowering operation on the entire filename would turn `MEOW.docx` into `meow.docx`.


### Example n
<!-- TODO: .. -->


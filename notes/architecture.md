Notes on High-Level Architecture
================================
Written 2017-08-17 by Jonas Sjöberg


Modular Design
==============
Roughly all program components generally fall under either one of two
categories; __core__ or __non-core__.

The idea is that the __non-core__-components should be "pluggable" and
"hotloaded" depending on availability and suitability.

It should be easy to add functionality and custom behaviour to the program,
communication between the *core* and *non-core* components should follow some
well-defined interface to allow the *core* to change without affecting the
*non-core* components.


Following a Sample Program Invocation
=====================================
The program will act on one or many files at once. The following processing
pipeline is executed for each given file.

Once again, with additional implementation details (some of which is still
unimplemented..) included:

1. Receive `input_path(s)` to process
    1. Find files to process, recursively if using `-r`/`--recurse`

2. Start iterating over the files in the list of files to process
   --- for each file, do;
    1. Construct a `FileObject` representing the file
    2. __Begin "data extraction"__ using an instance of `Extraction`
        1. Populate a queue with all extractor classes that "can handle" the
           file, which is determined by testing the file MIME-type.
        2. If the `Extraction` instance is told to include all extractors,
           include all. Otherwise, extractors that have a `is_slow` flag set is
           remove from the queue.


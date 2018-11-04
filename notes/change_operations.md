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
perform renaming tasks manually.

### Possibly beneficial effects of using this kind of system

* Might make future integration of machine learning techniques less messy.
* Reasoning about all changes in this way could simplify "collaboration"
  between parts of the program.
* Future multi-threading/parallelism might work better with some common
  abstract "chunk of work" that can be queued, awaited, etc.


### Illustrative Examples

#### Ill-defined Manipulation of Filename Substrings
Common scenario that we should be able to handle.

I would probably attempt to split the filename with some (trained?) tokenizer
and then attempt to detect any "named entities" *"name template field values"*
among the substrings, followed by performing some abstract and likely very
context-specific changes to finally arrive at some ill-defined desired result.

I've been thinking that this might be suitable for machine learning techniques
that picks up on *some* characteristics of the given file(s) and determines the
most likely changes to perform.

Assume none of these files contain meaningful content or metadata to work with:
```
~/example/foo.txt
~/example/foo (1).txt
~/example/2_foo.txt
```

Assume we do not populate a name template and that the only available
information is the full file paths.

We might use some machine learning technique that looks at a set of
characteristics. For simplicity, assume it only cares about parent directory
basename "`example`" .
When we tell `autonameow` to rename `~/example/*.txt`, it has never seen the
`example` signifier before and does not know what to do. Maybe it asks the user
for what the desired outcome should be and the user somehow responds that the
desired outcome looks like this:

```
~/example/foo.txt      ->  ~/example/0_foo.txt
~/example/foo (1).txt  ->  ~/example/1_foo.txt
~/example/2_foo.txt    ->  ~/example/2_foo.txt
```

Tokenizing the original filenames, with extensions left as-is:
```
foo.txt      ->  WORD.txt
foo (1).txt  ->  WORD PARENTHESIS NUMBER PARENTHESIS.txt
2_foo.txt    ->  NUMBER DELIMITER WORD.txt
```

The __"change operations" would represent this "filename delta" as a number of
"atomic" changes__, I.E. a number of steps performed to transform the original
filename to the desired filename.

Then the transformation of one the file names, `foo (1).txt  ->  1_foo.txt`,
would be described using "change operations" similar to this:

0. Starting with the original filename (ignoring the extension)
    ```
    basename : "foo (1)"
      tokens : WORD PARENTHESIS NUMBER PARENTHESIS
    ```

1. Perform "swap substrings" operation
    ```
    basename : "(1) foo"
      tokens : PARENTHESIS NUMBER PARENTHESIS WORD
    ```

2. Perform "remove substring(PARENTHESIS)" operation
    ```
    basename : "1 foo"
      tokens : NUMBER WORD
    ```

3. Perform "join by delimiter (`_`)" operation
    ```
    basename : "1_foo"
      tokens : NUMBER DELIMITER WORD
    ```

For each signifier, the machine learning system learns one example of change
operations per file matching that signifier.
Files that match a certain signifier might all use the exact same sequence of
change operations, some small variation of operations, or require completely
different sequence of change operations to arrive at the desired outcome.
Choice of signifier(s) would play a huge part in how well this would work.

Hopefully, accuracy would improve with time as `autonameow` renames files in
`~/example/` and the system homes in on the appropriate change operations.

Then when we tell `autonameow` to rename `~/example/*.txt` again with a new set
of files (assumed to be "similar" to the first batch, I.E. good choice of
signifier), the system has some idea on which change operations work because it
has learned from three different examples.

```
~/example/bar.txt      ->  ~/example/0_bar.txt
~/example/bar (1).txt  ->  ~/example/1_bar.txt
~/example/2_bar.txt    ->  ~/example/2_bar.txt
```

1. `~/example/bar.txt  ->  ~/example/0_bar.txt`

    ```
    "bar"        ->  "0_bar"
    WORD         ->  NUMBER DELIMITER WORD
    ```
    Change operations:
    1. Insert "template field"/substring NUMBER at position 0
    2. Populate NUMBER *(sub-task modeled in the same way!)*
    2. Join by delimiter

2. `~/example/bar (1).txt  ->  ~/example/1_bar.txt`

    ```
    "bar (1)"                            ->  "1_bar"
    WORD PARENTHESIS NUMBER PARENTHESIS  ->  NUMBER DELIMITER WORD
    ```
    Change operations:
    1. Swap substrings
    2. Remove substring(PARENTHESIS)
    3. Join by delimiter (`_`)

3. `~/example/2_bar.txt  ->  ~/example/2_bar.txt`

    ```
    "2_bar"                ->  "2_bar"
    NUMBER DELIMITER WORD  ->  NUMBER DELIMITER WORD
    ```
    Change operations:
    0. None are required!



### Example 2
Single "letter case lowering operation" acting on the entire filename would
turn `MEOW.docx` into `meow.docx`.


### Example n
<!-- TODO: .. -->

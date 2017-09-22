Notes on High-Level Architecture
================================
Written 2017-08-17 by Jonas Sjöberg

* Revised 2017-09-22 -- Added notes from `ideas.md`


Modular Design
==============
Roughly all program components generally fall under either one of two
categories; __core__ or __non-core__.

The idea is that the __non-core__-components should be "pluggable" and
"hotloaded" depending on availability and suitability.

It should be easy to add functionality and custom behavior to the program,
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
    2. __Begin "data extraction"__
        1. Gather all extractor classes that "can handle" the file,
           which is determined by testing the file MIME-type.
        2. If all results should be displayed, include all extractors.
           Otherwise, of the extractors that have the `is_slow` flag set,
           include only those referenced by the active configuration rules.
        3. Call each extractor in turn, passing the results back to the
           `SessionRepository`.
    3. __Begin "analysis"__
        1. Gather all analyzer classes the "can handle" the file,
           determined by the class methods `can_handle`.
        2. Run all analyzers in turn, passing the results back to the
           `SessionRepository`.
    4. __Run "plugins"__
        1. Gather all available plugins.
        2. Filter out plugins that "can handle" the file, determined by the
           class method `can_handle` of each plugin.
        3. Run all plugins in turn, passing the results back to the
           `SessionRepository`.
    5. __Run "rule matcher"__
        1. Get all rules from the active configuration.
        2. For each rule, do;
            1. Evaluate all rule conditions.
            2. Remove rules that require an exact match and any conditions
               evaluates false.
        3. For each remaining rule, do;
            1. Evaluate all rule conditions and calculate scores and weights
               based on the number of met conditions and the total number of
               conditions.
        4. Prioritize rules by score, weight and ranking bias.
        5. Store all prioritized rules as "candidates", presenting the highest
           priority rule as the "best match".
    6. __A) If running in "automagic" mode__
        1. Set the active name template to the name template defined in the
           "best matched" rule.
        2. Create an instance of `Resolver`
        3. Register each of the data sources defined in the "best matched" rule as a
           known source to the resolver.
        4. Check that all name template fields have been assigned a known source.

<!-- TODO: .. -->


On future frontends/GUIs
========================

### What is going on?

* __Program Operates on input:__ file(s)
* __Program Provides:__ New file names for the file(s)

Where/when are options presented and choices made?
Which could be presented in a GUI or in an *interactive mode*?

For any given file, how does the program come up with a new name?

What is required to come up with a new file name?

1. Select a __name template__
2. Populate the __placeholder fields__ in the template


#### Selecting a __name template__

* Chosen by the user
* Determined by the active configuration rule, chosen by the `RuleMatcher`

#### Populating the __placeholder fields__
How are the fields populated?

For each placeholder field, get some data that can be formatted to the fields
requirement (?).
The data could be either;

* Interactively chosen by the user
* Determined by the active configuration rule, chosen by the `RuleMatcher`

Which choices are presented to the user?
How are possible candidates collected?

`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Software Architecture
=====================
Notes on the High-Level Architecture of `autonameow`.

__NOTE: This information is not being kept up to date!__

#### Revisions
* 2017-08-17 --- `jonasjberg` Initial
* 2017-09-22 --- `jonasjberg` Added notes from `ideas.md`
* 2017-09-23 --- `jonasjberg` Merged with `2017-06-15_architecture.md`
* 2017-12-02 --- `jonasjberg` Remove old part. Add note that it is all old.
* 2017-12-15 --- `jonasjberg` Add section on "on demand" extraction.
* 2018-01-01 --- `jonasjberg` Update ..
* 2018-03-06 --- `jonasjberg` Ideas on constructing extractors declaratively
* 2018-03-26 --- `jonasjberg` Loading providers "lazily"


--------------------------------------------------------------------------------


Cleaning up the Provider Runners and Registries
-----------------------------------------------
> Jonas Sjöberg, 2018-03-26.

Current way of launching providers is pretty messy, especially regarding
setup and collection of classes and how/when the classes are instantiated.

### "Registries"
Providers are first handled as classes, which are collected and made available
from some kind of "registry".
When a provider is fetched from the "registry" for the first time, the class
should be instantiated and stored for re-use during any additional requests.
This would allow implementing `[TD0183]`. It also avoids redundantly re-loading
caches and setting up other provider-specific state that remains unchanged when
processing files.

### "Runners"
Each group of providers (extractors, analyzers) should be started by a "runner"
class.
The runner gets available providers (as class instances) from the registry.

### "Controllers"
Not quite sure about this yet.
The "runners" and "registries" would be bundled in light-weight "controller"
classes that would serve mainly to encapsulate the "runner" and "registry"
singletons and keep them out of global (module) scope.

### Other Considerations
Think about allowing for asynchronous/parallell running of providers.
However, this might currently not make much sense with the current "streaming"
way that providers are called upon sequentially, while evaluating conditions
and fetching data, etc..

### Related TODOs;

> * `[TD0185]` __Rework the highest level data request handler interface.__
>
>     * Don't pass the `master_provider` as a module. Use new "controller" class?
>     * Fix both global and direct references used to access the `Registry` and
>       `master_provider` functions.  
>       Some places access module-level functions directly after importing the
>       module, while some get a reference to the module passed in as an argument
>       (emanating from `Autonameow.master_provider`. Incomplete and forgotten?)
>
>     * Look at possibly wrapping up the pairs of "runner" and "registry" classes
>       in a "facade"-like controller class. Alternatively, just try to clean up
>       the current messy accessing.
>       Related notes:  `notes/2018-03-24-rough-architecture-sketch.jpg`
>
>     * Allow setting up (instantiating) provider classes once, then re-use the
>       instances when processing files.
>       Related to `[TD0183]` on using one `exiftool` process in "batch mode".
>
> * `[TD0183]` __Look into `exiftool` time-complexity.__  
>
>    The `ExiftoolMetadataExtractor` should be reworked to be instantiated once
>    at first use and then remain available for re-use for any additional
>    extraction. Make sure it is properly closed at program exit to prevent any
>    kind of resource leaks.
>
> * `[TD0126]` Clean up boundaries/interface to the `analyzers` package.
>
> * `[TD0151]` __Fix inconsistent use of classes vs. class instances.__  
>     Attributes of the provider classes are accessed both from uninstantiated
>     classes and class instances. The `metainfo()` method should be accessible
>     without first having to instantiate the class.


--------------------------------------------------------------------------------


Declarative Extractors through YAML files
-----------------------------------------
> Jonas Sjöberg, 2018-03-06.

The extractor `FIELD_LOOK` data was moved to external yaml files in commit
6a1707a7896bef2e151ce96de420a5f78652045a.

__How about moving all extractor code to YAML files?__

Assuming all extractors will use external programs do do the actual extraction,
the command-lines to execute could be specified in a yaml file.  This also goes
for any filtering and other kinds of special handling of specific fields in
specific extractors.

I came across an example of this in
`dbpedia_fact-extractor.git/date_normalizer/*`, where data and Python code is
declared in yaml-files which is then evaluated and used by the main program.

This should make things a lot cleaner and make development of additional
extractors a lot less complicated.  But it probably also will require a sound
YAML data format.

Pros:

* Simplifies and isolates extractor changes
* A lot less boilerplate

Cons:

* Executing arbitrary code in yaml files is a huge security vulnerability
* Arguably less "safe" due to interpreter doing *even less* validation before execution
* Messy if extractor must do some unforeseen or complex behaviour



Rethinking Requests and Gathering Required Data
===============================================
Currently, either all extractors are executed when "listing all results" or
only extractors that are "mapped" to MeowURIs that are referenced in the active
configuration are executed.

For performance and implementing coming features like evaluating conditions
like *"does the textual contents match this regular expression?"*, it would
probably make more sense to rethink data extraction to something more like
"streaming" and non-blocking/request-based;
__gathering only the data that is explicitly required.__

When evaluating a rule like;

> * Conditions:
>     1. MIME-type is `image/jpeg`
>     2. Textual contents match `meow*`
>
> * Exact match is required

Given a file `foo.pdf`, the first condition will fail and because the rule
requires all conditions to evaluate true, the entire rule should be discarded.

Rule evaluation should be aborted after the first failed condition, there is no
need to extract textual contents.


"Streaming" or "On-demand" Extraction
-------------------------------------
Example of rule evaluation using this proposed re-design, using a configuration;

> 1. Rule 1
>     * Conditions:
>         1. MIME-type is `image/jpeg`
>         2. Textual contents match `meow*`
>     * Exact match is required
> 2. Rule 2
>     * Conditions:
>         1. MIME-type is `application/*`
>         2. Textual contents match `meow*`
>     * Exact match is required

Rule evaluation would follow something like the following sequence of events.

* Given a file `foo.pdf`;
    * __Start evaluating Rule 1__
        * Start evaluating condition 1
            * Get data (MIME-type) required to evaluate condition 1
                * Execute extractor that can provide the required data.
            * Evaluate condition 1:  `application/pdf == image/jpeg`
            * Condition evaluates FALSE
    * __Discard Rule 1__
    * __Start evaluating Rule 2__
        * Start evaluating condition 1
            * Get __previously extracted data__ (MIME-type)
            * Evaluate condition 1:  `application/pdf == application/*`
            * Condition evaluates TRUE
        * Start evaluating condition 2
            * Extract data (textual contents) required to evaluate condition 2
                * Execute extractor that can provide the required data.
            * Evaluate condition 2:  `text.matches(meow*)`
            * Condition evaluates FALSE
    * __Discard Rule 2__ *(assuming the text does not match `meow*`)*

* Given a file `foo_bar.jpg`;
    * __Start evaluating Rule 1__
        * Start evaluating condition 1
            * Get data (MIME-type) required to evaluate condition 1
                * Execute extractor that can provide the required data.
            * Evaluate condition 1:  `image/jpeg == image/jpeg`
            * Condition evaluates TRUE.
        * Start evaluating condition 2
            * Extract data (textual contents) required to evaluate condition 2
                * Execute extractor that can provide the required data.
            * Evaluate condition 2:  `text.matches(meow*)`
            * Condition evaluates FALSE.
    * __Start evaluating Rule 2__
        * Start evaluating condition 1
            * Get __previously extracted data__ (MIME-type)
            * Evaluate condition 1:  `image/jpeg == application/*`
            * Condition evaluates FALSE.
    * __Discard Rule 2__


### Take-away Points

* Avoid preemptively extracting data that is not explicitly required.
* Re-use data that has been extracted previously.
* Instead of running extraction and rule evaluation as completely separate
  processes, gather data "on demand".


### Practical Concerns
If a rule condition requires a single piece of data, say `EXIF:CreateDate`, it
makes no sense to start the relevant provider (`exiftool`) and store *only this
single field* and discard the other metadata.  Rather, some requests for data
might make more data available as a side-effect if doing so results in a faster
overall execution time.


Update 2018-01-01
-----------------
Starting with a configuration file rule, with conditions;

```
CONDTIONS:
- data.identifier.string.A: expression_A
```

In order to test if this condition is true for the given file;

1. Get data that referred to by `data.identifier.string.A` ("`data_A`")
    * Parse `data.identifier.string.A`, find out which provider it maps to.
        * Check if this data has already been collected.
        * If not, run the provider and store all collected data.

2. Check condition by evaluating `expression_A(data_A)`
    * ...

3. Assuming the rule should be applied to the file;
    * Get name template placeholder fields from the name template.
    * For each name template field;
        * Check if the rule specifies a source for this field
            * Parse the source, `data.identifier.string.B`.
              Find out which provider it maps to.
                * Check if this data has already been collected.
                * If not, run the provider and store all collected data.
            * Validate the data, make sure it can be used to populate the field.
                * If not, mark it as unresolved.
                * If it is, mark it as resolved.



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

  1. ~~Receive `input_path(s)` to process~~
      1. ~~Find files to process, recursively if using `-r`/`--recurse`~~

  2. ~~Start iterating over the files in the list of files to process~~
   ~~--- for each file, do;~~
      1. ~~Construct a `FileObject` representing the file~~
      2. ~~__Begin "data extraction"__~~
          1. ~~Gather all extractor classes that "can handle" the file,~~
           ~~which is determined by testing the file MIME-type.~~
          2. ~~If all results should be displayed, include all extractors.~~
           ~~Otherwise, of the extractors that have the `is_slow` flag set,~~
           ~~include only those referenced by the active configuration rules.~~
          3. ~~Call each extractor in turn, passing the results back to the~~
           ~~`SessionRepository`.~~
      3. ~~__Begin "analysis"__~~
          1. ~~Gather all analyzer classes the "can handle" the file,~~
           ~~determined by the class methods `can_handle`.~~
          2. ~~Run all analyzers in turn, passing the results back to the~~
           ~~`SessionRepository`.~~
      4. __Run "rule matcher"__~~
          1. ~~Get all rules from the active configuration.~~
          2. ~~For each rule, do;~~
              1. ~~Evaluate all rule conditions.~~
              2. ~~Remove rules that require an exact match and any conditions~~
               ~~evaluates false.~~
          3. ~~For each remaining rule, do;~~
              1. ~~Evaluate all rule conditions and calculate scores and weights~~
               ~~based on the number of met conditions and the total number of~~
               ~~conditions.~~
          4. ~~Prioritize rules by score, weight and ranking bias.~~
          5. ~~Store all prioritized rules as "candidates", presenting the highest~~
           ~~priority rule as the "best match".~~
      5. ~~__A) If running in "automagic" mode__~~
          1. ~~Set the active name template to the name template defined in the~~
           ~~"best matched" rule.~~
          2. ~~Create an instance of `Resolver`~~
          3. ~~Register each of the data sources defined in the "best matched" rule as a~~
           ~~known source to the resolver.~~
          4. ~~Check that all name template fields have been assigned a known source.~~
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

### Working Backwards ..
.. to figure out where and if to place a "uncertainty boundary".
Which part of the program should only receive the single truth and not lists of
possible alternatives, etc.

Data pipeline in reverse order; working backwards from the final result:

1. __Name Builder__
    * Receives a name template string and a `field_data_map` dict:
        ```python
        field_data_map = {
            <class 'core.namebuilder.fields.Extension'>: <ExtractedData(
                PathComponent,
                mapped_fields=[
                    WeightedMapping(field=<class 'core.namebuilder.fields.Extension'>, weight=1)
                ],
                generic_field=None)(png)>,
            <class 'core.namebuilder.fields.Title'>: <ExtractedData(
                PathComponent,
                mapped_fields=[],
                generic_field=None)(simple-lexical-analysis)>
        }
        ```
      That is passed to `pre_assemble_format()` and then
      `_with_simple_string_keys()`, which turns it into:

        ```python
        data = {
            'extension': 'png',
            'title': 'simple-lexical-analysis'
        }
        ```
      This form is used to populate the name template string.

    * __The name builder should (does) receive unambigous, validated data__

2. __Resolver__
    * Receives the current `FileObject` and a name template string.
    * Generates a list of name template field classes from the name
      template string.
    * Data sources for template fields are added by calls to
      `add_known_sources()`.
    * *TODO: ..*

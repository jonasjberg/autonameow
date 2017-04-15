# `autonameow`

--------------------------------------------------------------------------------

Please refer to the [Product
Backlog](https://github.com/1dv430/js224eh-project/wiki/backlog) for a current
listing.

<!--
TODO-list
=========
List of things that need to be done.

### Bugs
- [x] Some of the date/time-information gets lost on the way to the new pretty
      output from `print_all_datetime_info(self)`.
- [x] Duplicate date/time from pdf metadata printed out by 
      `print_all_datetime_info(self)`. Not sure if the problem is in the data
      or inte the presentation ..
- [ ] Namebuilder implementation. Currently work in progress, incomplete code crash;

	  File "/home/spock/dev/projects/autoname/autonameow/__main__.py", line 26, in <module>
		autonameow.run()
	  File "/home/spock/dev/projects/autoname/autonameow/core/autonameow.py", line 113, in run
		self._handle_files()
	  File "/home/spock/dev/projects/autoname/autonameow/core/autonameow.py", line 159, in _handle_files
		name_builder.build()
	  File "/home/spock/dev/projects/autoname/autonameow/core/evaluate/namebuilder.py", line 72, in build
		fields = self._populate_fields(self.analysis_results, self.rule)
	  File "/home/spock/dev/projects/autoname/autonameow/core/evaluate/namebuilder.py", line 53, in _populate_fields
		ardate = get_datetime_by_alias(rule['prefer_datetime']).strftime('%Y-%m-%d')

      

### Wishlist
- [ ] Use configuration file(s) for settings program options.
    - [ ] Define file name templates.
    - [ ] Customized pattern matching.
    - [ ] Allow tweaking parser results sorting and ranking.
- [ ] GUI. Use the CLI base code as an API.
-->


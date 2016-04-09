import os


class fileObject(object):
    def __init__(self, date, time, description, filename = None, contents = None):
        self.date = date
        self.time = time
        self.description = description


        if filename is not None:
            # Remains untouched, for use when renaming file
            self.originalfilename = os.path.basename(filename)


        # Set of words derived from file content, can be used in a last ditch effort
        # to generate suggestions to field values.
        if contents is None:
            contents = {}
        self.contents = contents

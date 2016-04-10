import magic
import os


class FileObject(object):
    def __init__(self, path):
        #self.date = date
        #self.time = time
        #self.description = description
        


        if path is not None:
            # Remains untouched, for use when renaming file
            self.originalfilename = os.path.basename(path)


        # Set of words derived from file content, can be used in a last ditch effort
        # to generate suggestions to field values.
        #if contents is None:
        #    contents = {}
        #self.contents = contents


        # Get full absolute path
        self.path = os.path.abspath(path)

        # Figure out basic file type
        type = self.read_magic_header_bytes()
        # if type == "JPEG":
        #     print "will run image routine"
        #     # run_image_routine()
        # elif type == "PDF":
        #     print "will run pdf routine"
        # else:
        #     print "not sure what to do with file type"




    def read_magic_header_bytes(self):
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        type = ms.file(self.path)
        ms.close()
        return type.split()[0]

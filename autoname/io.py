import sys
import mimetypes

def determine_file_type(file):
    file_type=mimetypes.guess_type(file)
    print file_type

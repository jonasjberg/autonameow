import io
import logging

from unidecode import unidecode

from analyze.common import AnalyzerBase


class TextAnalyzer(AnalyzerBase):
    def __init__(self, file_object):
        self.file_object = file_object

        self.author = None
        self.title = None
        self.publisher = None

    def run(self):
        """
        Run this analyzer.
        This method is common to all analyzers.
        :return:
        """

        text_contents = self.extract_text_content()
        if text_contents:
            text_timestamps = self.get_datetime_from_text(text_contents)
            if text_timestamps:
                self.file_object.add_datetime(text_timestamps)

    def extract_text_content(self):
        """
        Extract the plain text contents of a text file as strings.
        :return: False or text content as strings
        """

        content = self.get_file_lines()
        # Fix encoding and replace Swedish characters.
        # content = content.encode('utf-8', 'ignore')
        # content = content.replace('\xc3\xb6', 'o').replace('\xc3\xa4', 'a').replace('\xc3\xa5', 'a')

        content = unidecode(content)
        # Collapse whitespace.
        # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
        content = " ".join(content.replace("\xa0", " ").strip().split())

        if content:
            # TODO: Determine what gets extracted **REALLY** ..
            logging.debug('Extracted [%s] words (??) of content' % len(content))
            return content
        else:
            logging.warn('Unable to extract PDF contents.')
            return None

    def get_datetime_from_text(self, text):

    def get_file_lines(self):
        fn = self.file_object.path
        with io.open(fn, 'r', encoding='utf8') as f:
            contents = f.read().split('\n')

            if contents:
                logging.info('Successfully read %d lines from \"%s\"'
                             % (len(contents), str(fn)))
                return contents
            else:
                logging.error("Got empty file \"%s\"" % fn)
                return None

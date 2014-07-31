"""
options module

Command-line input options and program help documentation.

"""

import os.path
import re
import sys
from conbib import __version__ as version


class CommandLineInput():
    """Digest the user-input and define runtime options."""
    def __init__(self):
        self._verify_input()
        self.mode = self._get_mode()
        self.input_file = self._get_input_file()
        self.output_file = self._get_output_file()

    def _verify_input(self):
        """Validate the user input."""
        if len(sys.argv) < 3:
            help_message = ('  convert-bibtex version %s\n'
                            '  Conversions and cite key generation for BibTeX files.\n\n'
                            '  Usage: convert-bibtex <mode> <input-file>\n\n'
                            '    <mode>     Description\n'
                            '    titlecase  Convert all titles to titlecase\n'
                            '    citekey    Generate cite keys for all entries\n'
                            '               according to the following scheme:\n'
                            '               <Last Author`s Last Name><2-Digit Year>_<Page Number OR Entry Type>\n\n'
                            '    <input-file> is a BibTeX .bib file that will not be overwritten'
                            % version)
            error(help_message)

    def _get_mode(self):
        """Get the mode in which the program should be run."""
        allowed_modes = ['titlecase', 'citekey', 'debug']
        mode = sys.argv[1]
        if mode in allowed_modes:
            return mode
        else:
            invalid_mode_message = ('  [ERROR] Invalid Mode\n'
                                    '          Allowed modes:'
                                    ' %s' % ', '.join(map(str, allowed_modes)))
            error(invalid_mode_message)
    
    def _get_input_file(self):
        """Get the LaTeX input file from command line."""
        file_to_convert = sys.argv[2]
        if os.path.exists(file_to_convert):
            return file_to_convert
        else:
            error("File `%s' does not exist" % file_to_convert)
    
    def _get_output_file(self):
        """Generate the output filename as `input_filename.mode.bib'."""
        components = self.input_file.rsplit('.', 1)
        output_file_name = '.'.join([components[0], self.mode, components[1]])
        return output_file_name


def error(message):
    """Print error message and terminate the program."""
    print str(message)
    sys.exit(0)

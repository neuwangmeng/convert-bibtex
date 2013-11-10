"""
convert
Conversions and cite key generation for BibTeX files.
"""

import os.path
import re
import sys

from conbib.titlecase import titlecase


__version__ = '0.2.a1'


def main():
    """Get user-input and perform requested operation."""
    options = CommandLineInput()
    if options.mode == 'titlecase':
        convert_title_to_titlecase(options.input_file, options.output_file)
    if options.mode == 'citekey':
        error('  Cite key generation coming soon')


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
            help_message = ('  convert-bibtex\n'
                            '  Conversions and cite key generation for BibTeX files.\n\n'
                            '  Usage: convert-bibtex <mode> <input-file>\n\n'
                            '    <mode>     Description\n'
                            '    titlecase  Convert all titles to titlecase\n'
                            '    citekey    Generate cite keys for all entries\n'
                            '               according to the following scheme:\n'
                            '               <Last Author`s Last Name><2-Digit Year>_<Page Number OR Entry Type>\n\n'
                            '    <input-file> is a BibTeX .bib file that will not be overwritten')
            error(help_message)

    def _get_mode(self):
        """Get the mode in which the program should be run."""
        allowed_modes = ['titlecase', 'citekey']
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
        """Generate the output filename as `input_filename.titlecase.bib'."""
        components = self.input_file.rsplit('.', 1)
        output_file_name = '.'.join([components[0], self.mode, components[1]])
        return output_file_name


def convert_title_to_titlecase(input_file, output_file):
    """Convert all titles in the `title' attribute of a Bib file to titlecase.
    
    This routine takes in a LaTeX .bib file and parses line-by-line searching
    for all `title' attributes of the bib items.  It converts all text
    associated with the `title' attribute to titlecase.  The original input
    .bib file is preserved and the new output written to
    `input_filename.titlecase.bib'.
    
    """
    print ('  Input file: %s\n  Output file: %s\n'
           '  Converting all title attributes to titlecase'
           % (input_file, output_file))
    out = open(output_file, 'w')
    items_updated = 0
    with open(input_file) as f:
        for line in f:
            if is_title(line):
                title = get_title(line)
                titlecase_title = make_titlecase_title(line) 
                out.write(titlecase_title)
                items_updated += 1
            else:
                out.write(line)
    out.close()
    print '  Updated %d Bib items' % items_updated 

def is_title(line):
    """Return True if line contains the title entry."""
    return is_item('title', line) 

def is_item(item, line):
    """Return True if current line contains item."""
    item_key = get_item_key(item) 
    return item_key.match(line)

def get_title(line):
    """Return the contents of the `title' attribute."""
    return get_attribute_item('title', 'contents', line)

def get_attribute_item(item, part, line):
    """Return the part of the attribute item for the given line. 
    
    This function returns one of three specified parts of the Bib item
    attribute:
        preffix    all text up to and including the `{'
        contents   all text between the `{' and `}'
        suffix     all text after and including the `}'
    
    """
    group_mapping = {'preffix': 1, 'contents': 2, 'suffix': 3}
    if part in group_mapping:
        group = group_mapping[part]
    else:
        error('Invalid part')

    item_key = get_item_key(item)
    item_key_match = is_item(item, line)

    if item_key_match:
        item = item_key_match.group(group)
    else:
        item = None
    return item

def get_item_key(item):
    """Return a regular expression object for matching Bib attribute item."""
    item = re.compile(r'(^\s*%s\s*=\s*\{?)(.+?)(\}?\,$)' % item, re.IGNORECASE)
    return item

def make_titlecase_title(line):
    """Return Bib item `title' attribute with title contents in titlecase."""
    title_preffix = get_attribute_item('title', 'preffix', line) 
    title_suffix = get_attribute_item('title', 'suffix', line)
    
    title_contents = get_title(line)
    title_contents = convert_to_titlecase(title_contents)

    title_attribute = ''.join([title_preffix,
                               title_contents,
                               title_suffix,
                               '\n'])
    return title_attribute

def convert_to_titlecase(text):
    """Convert text to titlecase."""
    return titlecase(text)

def error(message):
    """Print error message and terminate the program."""
    print str(message)
    sys.exit(0)

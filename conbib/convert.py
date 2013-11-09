#!/usr/bin/env python

"""
convert-bibtex
Convert titles in a LaTeX Bib file to title case.
"""

import os.path
import re
import sys

from conbib.titlecase import titlecase


def main():
    """Convert all titles in the `title' attribute of a Bib file to titlecase.
    
    This routine takes in a LaTeX .bib file and parses line-by-line searching
    for all `title' attributes of the bib items.  It converts all text
    associated with the `title' attribute to titlecase.  The original input
    .bib file is preserved and the new output written to
    `input_filename.titlecase.bib'.
    
    """
    input_file = get_input_file()
    print 'Input file: %s' % input_file
    output_file = get_output_file(input_file)
    print 'Output file: %s' % output_file
    out = open(output_file, 'w')
    print 'Converting all title attributes to titlecase'
    count = 0
    with open(input_file) as f:
        for line in f:
            if is_title(line):
                title = get_title(line)
                titlecase_title = make_titlecase_title(line) 
                out.write(titlecase_title)
                count += 1
            else:
                out.write(line)
    out.close()
    print 'Updated %d Bib items' % count

def get_input_file():
    """Get the LaTeX input file from command line."""
    if len(sys.argv) > 1:
        file_to_convert = sys.argv[1]
        if os.path.exists(file_to_convert):
            return file_to_convert
        else:
            error("File `%s' does not exist" % file_to_convert)
    else:
        error('Please specify an input file')

def get_output_file(input_file):
    """Generate the output filename as `input_filename.titlecase.bib'."""
    components = input_file.rsplit('.', 1)
    output_file_name = '.'.join([components[0], 'titlecase', components[1]])
    return output_file_name

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

if __name__ == '__main__':
    main()

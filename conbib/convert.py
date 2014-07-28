"""
convert module

The main functions for converting titles to titlecase and generating citekeys
are cotained within this module.

"""

import re
import sys
import os.path

from conbib.bibitem import * 
from conbib.titlecase import titlecase
from conbib.options import CommandLineInput, error


def convert_to_titlecase(text):
    """Return string with text converted to titlecase format."""
    return titlecase(text)


def _update_citekeys(input_file, output_file):
    """Update all bibitem citekeys in input_file.
    
    This routine takes in a LaTeX .bib file and constructs citekeys for each
    bib item.  The original input .bib file is preserved and the new output
    written to `input_filename.citekey.bib'.

    The citekey format is defined in the _make_citekey() function below.
    
    """
    print ('  Input file: %s\n  Output file: %s\n'
           '  Updating bib item cite keys...'
           % (input_file, output_file))
    bibitems = get_bibitems(input_file)
    missing_items = bibitems.pop()
    out = open(output_file, 'w')
    items_updated = 0
    with open(input_file, 'rU') as f:
        for line in f:
            if is_bibitem(line):
                citekey = _make_citekey(bibitems[items_updated])
                bibitem = '@%s{%s,\n' % (bibitems[items_updated].bibtype,
                                         citekey)
                out.write(bibitem)
                items_updated += 1
            else:
                out.write(line)
    out.close()
    print '  Updated %d Bib items' % items_updated 
    missing_items.report_missing_items()


def _make_citekey(bibitem):
    """Make the citekey for the given bibitem.

    Current Format: [LastAuthorLastName][2-digitYear]_[FirstPage]

    If the type is not 'article' then [FirstPage] is replaced with [Type],
    except for 'phdthesis' and 'mastersthesis', which are replaced with
    'thesis'.

    """
    last_author_last_name = bibitem.get_last_author_last_name()
    two_digit_year = bibitem.get_2d_year()

    citekey = ''.join([last_author_last_name, two_digit_year])

    if bibitem.bibtype == 'article':
        first_page = bibitem.get_first_page()
        citekey = '_'.join([citekey, first_page])
    elif bibitem.bibtype == 'phdthesis' or bibitem.bibtype == 'mastersthesis':
        citekey = '_'.join([citekey, 'thesis'])
    else:
        citekey = '_'.join([citekey, bibitem.bibtype])
    return citekey


def _make_titlecase_title(line):
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


def _convert_titles_to_titlecase(input_file, output_file):
    """Convert all titles in the `title' attribute of a Bib file to titlecase.
    
    This routine takes in a LaTeX .bib file and parses line-by-line searching
    for all `title' attributes of the bib items.  It converts all text
    associated with the `title' attribute to titlecase.  The original input
    .bib file is preserved and the new output written to
    `input_filename.titlecase.bib'.
    
    """
    print ('  Input file: %s\n  Output file: %s\n'
           '  Converting title attributes to titlecase...'
           % (input_file, output_file))
    out = open(output_file, 'w')
    items_updated = 0
    with open(input_file, 'rU') as f:
        for line in f:
            if is_title(line):
                title = get_title(line)
                titlecase_title = _make_titlecase_title(line) 
                out.write(titlecase_title)
                items_updated += 1
            else:
                out.write(line)
    out.close()
    print '  Updated %d Bib items' % items_updated 


def main():
    """Get user-input and perform requested operation."""
    options = CommandLineInput()
    if options.mode == 'titlecase':
        _convert_titles_to_titlecase(options.input_file, options.output_file)
    if options.mode == 'citekey':
        _update_citekeys(options.input_file, options.output_file)
    if options.mode == 'debug':
        bibitems = get_bibitems(options.input_file, False)
        list_bibitems(bibitems)

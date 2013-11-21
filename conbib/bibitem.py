"""
bibitem module

This module contains the BibItem class with methods for generating the Li
group's standard citekey.  This module also contains several functions for
parsing a LaTeX bib file including functions for matching and returning the
contents of various bib item attributes. 

"""

import re
import sys
import os.path

__all__ = ['is_bibitem',
           'is_bibitem_end',
           'is_author',
           'is_title',
           'is_booktitle',
           'is_journal',
           'is_volume',
           'is_year',
           'is_pages',
           'is_item',
           'get_bibitem_type',
           'get_author',
           'get_title',
           'get_booktitle',
           'get_journal',
           'get_volume',
           'get_year',
           'get_pages',
           'get_bibitems',
           'get_item_key',
           'get_attribute_item',
           'list_bibitems']

# These are the allowe BibItem entry types, currently supported by BiBTeX.
ENTRY_TYPES = ['article',
               'book',
               'booklet',
               'conference',
               'inbook',
               'incollection',
               'inproceedings',
               'manual',
               'mastersthesis',
               'misc',
               'phdthesis',
               'proceedings',
               'techreport',
               'unpublished']


class BibItem():
    """Main bibiligraphy item class."""
    def __init__(self, inputfile, missing=None):
        """Construct object by parsing single bibitem in inputfile.
        
        The input file should be a standard Python file object.  As the object
        is initialized, it will advance through the inputfile until one full
        bibitem is digested.

        The found flag is used to prevent parsing more than one bibitem.
        Once a bibitem is found, this flag is set to True in order to exit the
        loop once a blank line is encountered in the inputfile.

        """
        self.found = False
        self.author = None
        self.title = None
        self.journal = None
        self.volume = None
        self.year = None
        self.pages = None
        self.missing = missing

        for line in inputfile:
            if is_bibitem(line):
                self.found = True
                self.bibtype = get_bibitem_type(line)
            
            elif is_author(line):
                self.author = get_author(line)
            
            elif is_title(line):
                self.title = get_title(line)

            elif is_booktitle(line):
                self.title = get_booktitle(line)
            
            elif is_journal(line):
                self.journal = get_journal(line)
            
            elif is_volume(line):
                self.volume = get_volume(line)
            
            elif is_year(line):
                self.year = get_year(line)
            
            elif is_pages(line):
                self.pages = get_pages(line)

            # If a bibitem is found and we encounter an attribute not parsed
            # above, then skip to the next line
            elif self.found and not is_bibitem_end(line):
                continue

            # If a bibitem is not found and we encounter a blank line or an
            # end-of-bibitem character (`}'), then skip to the next line
            elif not self.found and is_bibitem_end(line):
                continue

            # Lastly, if an item was found and we encounter a blank line or
            # end-of-bibitem character, then exit the loop, we have a bibitem
            else:
                break

    def get_last_author_last_name(self):
        """Return the last author's last name.

        The LaTeX bib file allows for two types of author entries:

            (1) author = {Joseph W. May and X. Li},

            (2) author = {May, Joseph W. and Li, X.},

        The first and middle names may be written out completely or
        abbreviated.  All names are separated by 'and'.  The first/middle names
        can occur before the last name, or they may appear after the last name
        permitted there is a comma after the last name.

        This parser handles both of these cases by using the following
        splitting scheme on the author attribute:

            [1] split using 'and' as the delimiter
            
            [2] check if there is a comma, if so, then split using ',' as the
                delimiter
            
            [3] if there are no commas, split using ' ' as the delimiter

        For last names such as 'van Kuiken', only 'Kuiken' will be returned.

        """
        if self.author:
            split_with_and = self.author.split(' and ')
            
            # We now have the last author
            last_author = split_with_and.pop()

            # Extract the last name based on presence/absence of a comma
            comma = re.compile(r'^(.+),.+')
            match_comma = comma.match(last_author)
            if match_comma:
                last_name = match_comma.group(1).strip()
                # One last step to remove last name prefix (i.e., 'van Kuiken')
                split_with_space = last_name.split()
                last_name = split_with_space.pop()
            else:
                split_with_space = last_author.split()
                last_name = split_with_space.pop()
            return last_name
        else:
            if self.missing:
                self.missing.add('Last Name')
            return 'MISSING'

    def get_2d_year(self):
        """Return string containing the 2-digit year.

        Example: if the year is '2013', this method returns '13'.

        """
        if self.year:
            return self.year[2:]
        else:
            if self.missing:
                self.missing.add('Year')
            return 'MISSING'

    def get_first_page(self):
        """Return string containing the first page in the pages range."""
        if self.pages:
            return self.pages.split('-')[0]
        else:
            if self.missing:
                self.missing.add('Page Number')
            return 'MISSING'


class _MissingAttribute():
    """Missing information tracker for bibitems.
    
    This class stores information regarding missing attributes for all bibitems
    in a given bibfile.
    
    """
    def __init__(self):
        self.is_missing = False
        self.missing_items = {}

    def add(self, attribute):
        self.is_missing = True
        if attribute in self.missing_items: 
            self.missing_items[attribute] += 1
        else:
            self.missing_items[attribute] = 1

    def report_missing_items(self):
        if self.is_missing:
            warning = ('  \n'
                       '  *** WARNING ***\n'
                       '  Some citekeys are incomplete due to missing information\n'
                       '  Check your .bib file for the following missing items:\n'
                       '     ------------------------------\n'
                       '     %-20s  %8s\n'
                       '     ------------------------------'
                       % ('Missing Item', 'Count'))
            print warning
            for attr,num in self.missing_items.iteritems():
                print '     %-20s  %8d' % (attr, num)
            print '     ------------------------------'


# The functions below are used to parse the bib file.  They are included as
# functions rather than methods of the BibItem class so that they may be
# imported as individual functions for line-by-line parsing of a bib file.  For
# instance, if all you want to update are the titles of a bib file while
# leaving all other information intact, you wouldn't need to create individual
# BibItem objects, but rather, only parse the bib file for the title attribute.

def is_author(line):
    """Return True if line contains the author entry."""
    return is_item('author', line)


def is_title(line):
    """Return True if line contains the title entry."""
    return is_item('title', line) 


def is_booktitle(line):
    """Return True if line contains the booktitle entry."""
    return is_item('booktitle', line) 


def is_journal(line):
    """Return True if line contains the journal entry."""
    return is_item('journal', line) 


def is_volume(line):
    """Return True if line contains the volume entry."""
    return is_item('volume', line) 


def is_year(line):
    """Return True if line contains the year entry."""
    return is_item('year', line) 


def is_pages(line):
    """Return True if line contains the pages entry."""
    return is_item('pages', line) 


def get_author(line):
    """Return the contents of the `author' attribute."""
    return get_attribute_item('author', 'contents', line)


def get_title(line):
    """Return the contents of the `title' attribute."""
    return get_attribute_item('title', 'contents', line)


def get_booktitle(line):
    """Return the contents of the `booktitle' attribute."""
    return get_attribute_item('booktitle', 'contents', line)


def get_journal(line):
    """Return the contents of the `journal' attribute."""
    return get_attribute_item('journal', 'contents', line)


def get_volume(line):
    """Return the contents of the `volume' attribute."""
    return get_attribute_item('volume', 'contents', line)


def get_year(line):
    """Return the contents of the `year' attribute."""
    return get_attribute_item('year', 'contents', line)


def get_pages(line):
    """Return the contents of the `pages' attribute."""
    return get_attribute_item('pages', 'contents', line)


def get_bibitem_type(line):
    """Return the bibitem type proceeding the `@' character."""
    allowed_entries = '|'.join(ENTRY_TYPES)
    item_type = re.compile(r'^@(%s)\{' % allowed_entries)
    item_type_match = item_type.match(line)
    if item_type_match:
        return item_type_match.group(1)
    return None


def is_bibitem(line):
    """Return True if line contains the start of a new bibitem."""
    allowed_entries = '|'.join(ENTRY_TYPES)
    start_character = re.compile(r'^@(%s)' % allowed_entries)
    return start_character.match(line)


def is_bibitem_end(line):
    """Return True if line is end of bibitem: new line or single `}'."""
    item_end = re.compile(r'^\s*}\n|^\s*$')
    return item_end.match(line)


def get_item_key(item):
    """Return regular expression object for matching Bib attribute item."""
    item = re.compile(r'(^\s*%s\s*=\s*\{?)(.+?)(\}?\,?$)' % item,
                      re.IGNORECASE)
    return item


def is_item(item, line):
    """Return True if current line contains item."""
    item_key = get_item_key(item) 
    return item_key.match(line)


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
        error('Invalid part given to get_attribute_item')

    item_key = get_item_key(item)
    item_key_match = is_item(item, line)

    if item_key_match:
        item = item_key_match.group(group)
    else:
        item = None
    return item


def get_file_length(filename):
    """Return the number of lines in filename."""
    with open(filename, 'rU') as filein:
            lines = sum(1 for line in filein)
    return lines


def get_bibitems(input_filename, record_missing=True):
    """Return a list of all bibitems as BibItem objects.
    
    The last item in the list is an instance of the MissingAttributes class.

    """
    bibitems = []
    missing = _MissingAttribute()
    file_length = get_file_length(input_filename)
    with open(input_filename, 'rU') as bibfile:
        for i in range(file_length):
            item = BibItem(bibfile, missing)
            if item.found:
                bibitems.append(item)
    if record_missing:
        bibitems.append(missing)
    return bibitems


def list_bibitems(bibitems):
    """Given a list of BibItem objects, print all attributes for each item."""
    print 'TOTAL NUMBER OF BIBITEMS: %d' % len(bibitems)
    item_num = 1
    for item in bibitems:
        print '<<<>>> BIBITEM %d <<<>>>' % item_num
        print 'TYPE:    %s' % item.bibtype
        print 'AUTHOR:  %s' % item.author
        print 'TITLE:   %s' % item.title
        print 'JOURNAL: %s' % item.journal
        print 'VOLUME:  %s' % item.volume
        print 'YEAR:    %s' % item.year
        print 'PAGES:   %s' % item.pages
        print 'LALN:    %s' % item.get_last_author_last_name()
        print '2D-YEAR: %s' % item.get_2d_year()
        print '1ST PG:  %s' % item.get_first_page()
        print '\n'
        item_num += 1

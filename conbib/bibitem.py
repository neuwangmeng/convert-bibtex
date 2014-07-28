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
           'is_item',
           'is_address',
           'is_annote',
           'is_author',
           'is_booktitle',
           'is_chapter',
           'is_crossref',
           'is_edition',
           'is_editor',
           'is_eprint',
           'is_howpublished',
           'is_institution',
           'is_journal',
           'is_key',
           'is_month',
           'is_note',
           'is_number',
           'is_organization',
           'is_pages',
           'is_publisher',
           'is_school',
           'is_series',
           'is_title',
           'is_type',
           'is_url',
           'is_volume',
           'is_year',
           'get_bibitem_type',
           'get_bibitems',
           'get_item_key',
           'get_attribute_item',
           'get_address',
           'get_annote',
           'get_author',
           'get_booktitle',
           'get_chapter',
           'get_crossref',
           'get_edition',
           'get_editor',
           'get_eprint',
           'get_howpublished',
           'get_institution',
           'get_journal',
           'get_key',
           'get_month',
           'get_note',
           'get_number',
           'get_organization',
           'get_pages',
           'get_publisher',
           'get_school',
           'get_series',
           'get_title',
           'get_type',
           'get_url',
           'get_volume',
           'get_year',
           'list_bibitems']


# the allowed BibTeX entry types
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

        # BibTeX field types taken from http://en.wikipedia.org/wiki/BibTeX
        self.address = None
        self.annote = None
        self.author = None
        self.booktitle = None
        self.chapter = None
        self.crossref = None
        self.edition = None
        self.editor = None
        self.eprint = None
        self.howpublished = None
        self.institution = None
        self.journal = None
        self.key = None
        self.month = None
        self.note = None
        self.number = None
        self.organization = None
        self.pages = None
        self.publisher = None
        self.school = None
        self.series = None
        self.title = None
        self.type = None
        self.url = None
        self.volume = None
        self.year = None

        self.missing = missing

        for line in inputfile:
            if is_bibitem(line):
                self.found = True
                self.bibtype = get_bibitem_type(line)
            
            elif is_address(line):
                self.address = get_address(line)

            elif is_annote(line):
                self.annote = get_annote(line)
            
            elif is_author(line):
                self.author = get_author(line)
            
            elif is_booktitle(line):
                self.booktitle = get_booktitle(line)

            elif is_chapter(line):
                self.chapter = get_chapter(line)

            elif is_crossref(line):
                self.crossref = get_crossref(line)

            elif is_edition(line):
                self.edition = get_edition(line)

            elif is_editor(line):
                self.editor = get_editor(line)

            elif is_eprint(line):
                self.eprint = get_eprint(line)

            elif is_howpublished(line):
                self.howpublished = get_howpublished(line)

            elif is_institution(line):
                self.institution = get_institution(line)
            
            elif is_journal(line):
                self.journal = get_journal(line)
            
            elif is_key(line):
                self.key = get_key(line)

            elif is_month(line):
                self.month = get_month(line)

            elif is_note(line):
                self.note = get_note(line)

            elif is_number(line):
                self.number = get_number(line)

            elif is_organization(line):
                self.organization = get_organization(line)

            elif is_pages(line):
                self.pages = get_pages(line)

            elif is_publisher(line):
                self.publisher = get_publisher(line)

            elif is_school(line):
                self.school = get_school(line)

            elif is_series(line):
                self.series = get_series(line)

            elif is_title(line):
                self.title = get_title(line)

            elif is_type(line):
                self.type = get_type(line)

            elif is_url(line):
                self.url = get_url(line)

            elif is_volume(line):
                self.volume = get_volume(line)
            
            elif is_year(line):
                self.year = get_year(line)

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

    def get_last_author_last_name(self, escape=True, hyphenate=False):
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

        With ``escape`` set to True, LaTeX special character encodings will be
        removed.  For example, the following will be output regardless of the
        encoding style:
            
            \vZuti\'c      -->  Zutic
            \v{Z}uti\'{c}  -->  Zutic
            {\vZ}uti{\'c}  -->  Zutic

        With ``hyphenate`` set to False, hyphens in the name will be preserved.
        Otherwise, hyphens will be removed from the name.

        """
        # If no author list give, use the editor list, otherwise, report item
        # as 'MISSING'
        if self.author:
            author = self.author
        elif self.editor:
            author = self.editor
        else:
            if self.missing:
                self.missing.add('Last Name')
            return 'MISSING'

        split_with_and = author.split(' and ')
        # Temporary fix for author lists that span mulitple lines.
        # Currently, only the first line of author names will be parsed,
        # and the last author from that list will be used for cite key
        # generation.
        split_with_and = filter(None, split_with_and)
        
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
        
        # Sanitize the last name for citekey generation
        if escape:
            last_name = escape_encoding(last_name)
        if not hyphenate:
            last_name = last_name.translate(None, '-')
        return last_name

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
                       '  Check your .bib file for the following missing items by\n'
                       '  searching for "MISSING" in the output file:\n'
                       '  ------------------------------\n'
                       '  %-20s  %8s\n'
                       '  ------------------------------'
                       % ('Missing Item', 'Count'))
            print warning
            for attr,num in self.missing_items.iteritems():
                print '  %-20s  %8d' % (attr, num)
            print '  ------------------------------'


# The functions below are used to parse the bib file.  They are included as
# functions rather than methods of the BibItem class so that they may be
# imported as individual functions for line-by-line parsing of a bib file.  For
# instance, if all you want to update are the titles of a bib file while
# leaving all other information intact, you wouldn't need to create individual
# BibItem objects, but rather, only parse the bib file for the title attribute.

def is_address(line):
    """Return True if line contains the address entry."""
    return is_item('address', line)


def is_annote(line):
    """Return True if line contains the annote entry."""
    return is_item('annote', line)


def is_author(line):
    """Return True if line contains the author entry."""
    return is_item('author', line)


def is_booktitle(line):
    """Return True if line contains the booktitle entry."""
    return is_item('booktitle', line) 


def is_chapter(line):
    """Return True if line contains the chpater entry."""
    return is_item('chapter', line) 


def is_crossref(line):
    """Return True if line contains the crossref entry."""
    return is_item('crossref', line) 


def is_edition(line):
    """Return True if line contains the edition entry."""
    return is_item('edition', line) 


def is_editor(line):
    """Return True if line contains the editor entry."""
    return is_item('editor', line) 


def is_eprint(line):
    """Return True if line contains the eprint entry."""
    return is_item('eprint', line) 


def is_howpublished(line):
    """Return True if line contains the howpublished entry."""
    return is_item('howpublished', line) 


def is_institution(line):
    """Return True if line contains the institution entry."""
    return is_item('institution', line) 


def is_journal(line):
    """Return True if line contains the journal entry."""
    return is_item('journal', line) 


def is_key(line):
    """Return True if line contains the key entry."""
    return is_item('key', line) 


def is_month(line):
    """Return True if line contains the month entry."""
    return is_item('month', line) 


def is_note(line):
    """Return True if line contains the note entry."""
    return is_item('note', line) 


def is_number(line):
    """Return True if line contains the number entry."""
    return is_item('number', line) 


def is_organization(line):
    """Return True if line contains the organization entry."""
    return is_item('organization', line) 


def is_pages(line):
    """Return True if line contains the pages entry."""
    return is_item('pages', line) 


def is_publisher(line):
    """Return True if line contains the publisher entry."""
    return is_item('publisher', line) 


def is_school(line):
    """Return True if line contains the school entry."""
    return is_item('school', line) 


def is_series(line):
    """Return True if line contains the series entry."""
    return is_item('series', line) 


def is_title(line):
    """Return True if line contains the title entry."""
    return is_item('title', line) 


def is_type(line):
    """Return True if line contains the type entry."""
    return is_item('type', line) 


def is_url(line):
    """Return True if line contains the url entry."""
    return is_item('url', line) 


def is_volume(line):
    """Return True if line contains the volume entry."""
    return is_item('volume', line) 


def is_year(line):
    """Return True if line contains the year entry."""
    return is_item('year', line) 


def get_address(line):
    """Return the contents of the `address' attribute."""
    return get_attribute_item('address', 'contents', line)


def get_annote(line):
    """Return the contents of the `annote' attribute."""
    return get_attribute_item('annote', 'contents', line)


def get_author(line):
    """Return the contents of the `author' attribute."""
    return get_attribute_item('author', 'contents', line)


def get_booktitle(line):
    """Return the contents of the `booktitle' attribute."""
    return get_attribute_item('booktitle', 'contents', line)


def get_chapter(line):
    """Return the contents of the `chapter' attribute."""
    return get_attribute_item('chapter', 'contents', line)


def get_crossref(line):
    """Return the contents of the `crossref' attribute."""
    return get_attribute_item('crossref', 'contents', line)


def get_edition(line):
    """Return the contents of the `edition' attribute."""
    return get_attribute_item('edition', 'contents', line)


def get_editor(line):
    """Return the contents of the `editor' attribute."""
    return get_attribute_item('editor', 'contents', line)


def get_eprint(line):
    """Return the contents of the `eprint' attribute."""
    return get_attribute_item('eprint', 'contents', line)


def get_howpublished(line):
    """Return the contents of the `howpublished' attribute."""
    return get_attribute_item('howpublished', 'contents', line)


def get_institution(line):
    """Return the contents of the `institution' attribute."""
    return get_attribute_item('institution', 'contents', line)


def get_journal(line):
    """Return the contents of the `journal' attribute."""
    return get_attribute_item('journal', 'contents', line)


def get_key(line):
    """Return the contents of the `key' attribute."""
    return get_attribute_item('key', 'contents', line)


def get_month(line):
    """Return the contents of the `month' attribute."""
    return get_attribute_item('month', 'contents', line)


def get_note(line):
    """Return the contents of the `note' attribute."""
    return get_attribute_item('note', 'contents', line)


def get_number(line):
    """Return the contents of the `number' attribute."""
    return get_attribute_item('number', 'contents', line)


def get_organization(line):
    """Return the contents of the `organization' attribute."""
    return get_attribute_item('organization', 'contents', line)


def get_pages(line):
    """Return the contents of the `pages' attribute."""
    return get_attribute_item('pages', 'contents', line)


def get_publisher(line):
    """Return the contents of the `publisher' attribute."""
    return get_attribute_item('publisher', 'contents', line)


def get_school(line):
    """Return the contents of the `school' attribute."""
    return get_attribute_item('school', 'contents', line)


def get_series(line):
    """Return the contents of the `series' attribute."""
    return get_attribute_item('series', 'contents', line)


def get_title(line):
    """Return the contents of the `title' attribute."""
    return get_attribute_item('title', 'contents', line)


def get_type(line):
    """Return the contents of the `type' attribute."""
    return get_attribute_item('type', 'contents', line)


def get_url(line):
    """Return the contents of the `url' attribute."""
    return get_attribute_item('url', 'contents', line)


def get_volume(line):
    """Return the contents of the `volume' attribute."""
    return get_attribute_item('volume', 'contents', line)


def get_year(line):
    """Return the contents of the `year' attribute."""
    return get_attribute_item('year', 'contents', line)


def get_bibitem_type(line):
    """Return the bibitem type proceeding the `@' character."""
    allowed_entries = '|'.join(ENTRY_TYPES)
    item_type = re.compile(r'^@(%s)\s*\{' % allowed_entries)
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
    item = re.compile(r'(^\s*%s\s*=\s*\{?)(.+?)(\}\,?)' % item,
                      re.IGNORECASE)
    return item


def is_item(item, line):
    """Return regular expression match object if current line contains item."""
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
    missing = _MissingAttribute() if record_missing else None
    file_length = get_file_length(input_filename)
    with open(input_filename, 'rU') as bibfile:
        for i in range(file_length):
            item = BibItem(bibfile, missing)
            if item.found:
                bibitems.append(item)
    if record_missing:
        bibitems.append(missing)
    return bibitems


def escape_encoding(text):
    encodings = re.compile(r'\\[Hbcdklortuv`\'\^"~=\.]{1}')
    escaped_text = text.translate(None, '{}')
    escaped_text = encodings.sub('', escaped_text)
    return escaped_text


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

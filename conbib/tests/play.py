#!/usr/bin/env python

# Playground for the ``bibtexparser`` module.

#from pprint import pprint
#
#from bibtexparser.bparser import BibTexParser
#from bibtexparser.customization import homogeneize_latex_encoding 
#from bibtexparser.bwriter import to_bibtex
#
#with open('small.test.bib', 'r') as bibfile:
#    bp = BibTexParser(bibfile.read(), customization=homogeneize_latex_encoding)
#    pprint(bp.get_entry_list())
#
#output = to_bibtex(bp)

# Testing RE patterns for encoding capturing

import re


def out(num, param):
    print '  style%s = %s' % (num, param)


def escape_encoding(text):
    encodings = re.compile(r'\\[Hbcdklortuv`\'\^"~=\.]{1}')
    escaped_text = text.translate(None, '{}')
    escaped_text = encodings.sub('', escaped_text)
    return escaped_text


def main():
    # STEP 0
    style1 = r"\`s\'a\^t\"i\Hs\~f\ca\kc\l\=t\bo\.r\di\rn\ue\vs\ts\o"
    style2 = r"\`{s}\'{a}\^{t}\"{i}\H{s}\~{f}\c{a}\k{c}\l\={t}\b{o}\.{r}\d{i}\r{n}\u{e}\v{s}\t{s}\o"
    style3 = r"{\`s}{\'a}{\^t}{\"i}{\Hs}{\~f}{\ca}{\kc}{\l}{\=t}{\bo}{\.r}{\di}{\rn}{\ue}{\vs}{\ts}{\o}"
    
    print 'ORIGINAL'
    out('1', style1)
    out('2', style2)
    out('3', style3)
    
    
    # ESCAPE
    style1 = escape_encoding(style1)
    style2 = escape_encoding(style2)
    style3 = escape_encoding(style3)

    print 'FINAL'
    out('1', style1)
    out('2', style2)
    out('3', style3)


if __name__ == "__main__":
    main()

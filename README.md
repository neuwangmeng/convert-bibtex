convert-bibtex
==============

Conversions and cite key generation for BibTeX files.

About
-----

This program implements the BibItem class and functions for parsing BibTeX
files.  Individual bibliography items and a selection of their attributes are
parsed and stored as BibItem objects.  The `convert-bibtex` script is provided
for converting all titles to titlecase and for generating citation keys
according to the Li research group format.


Usage
-----

This program currently supports two modes:

* **titlecase**: convert all titles to titlecase
* **citekey**: generate cite keys for all entries according to
`<Last Author's Last Name><2-Digit Year>_<First Page Number OR Entry Type>`

To run the program, excute the following command:
`convert-bibtex <mode> <input-file>`, where `<mode>` is one of the options
listed above and `<input-file>` is the .bib file to be converted.  Your input
file will not be overwritten, but rahter, a new file named `input-file.mode.bib`
will be generated.


Installation
------------

1. Download the most recent release version as a gzipped tarball from the
`dist/` directory.
2. Unpack the tarball using `tar -xzvf convert-bibtex-X.X.tar.gz`.
3. Enter into the `convert-bibtex-X.X/` directory.
4. To install the program into the appropriate directory for third-party modules
in your Python installation, run the following command: `sudo python setup.py
install`.  You will be prompted for your password.
5. Close and re-open your terminal window.  The `convert-bibtex` program is now
installed.

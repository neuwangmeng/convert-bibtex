#!/usr/bin/env python

"""Test the titlecase conversion."""

import unittest
import conbib.convert

class TestTitlecase(unittest.TestCase):

    def test_titlecase(self):
        # test conversion of title attribute to titlecase
        self.title = 'this is a title in need of conversion'
        self.expected = 'This Is a Title in Need of Conversion'
        self.converted_title = conbib.convert.convert_to_titlecase(self.title)
        self.assertEqual(self.expected, self.converted_title)


if __name__ == '__main__':
    unittest.main()

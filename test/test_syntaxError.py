"""This file is a hack: files using the 'with' syntax will raise a syntax error on pre 2.4, so
these are placed here."""
from __future__ import with_statement
import warnings
from test_util import *

from matrix2latex import matrix2latex
def test_format_formatColumn_Warning():
    # Test for warning: http://stackoverflow.com/a/3892301/1942837
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always") # Cause all warnings to always be triggered.
        # specify both format and formatColumn
        t = matrix2latex([[123456e10, 123456e10]],
                             format='%g', formatColumn=['%.1g', '%g'])
        assert len(w) == 1
        assert issubclass(w[-1].category, Warning)
        assertEqual(t, 'format_formatColumn_Warning')            

"""This file is part of matrix2latex.

matrix2latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

matrix2latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with matrix2latex. If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ['matrix2latex']

try:
    from matrix2latex import matrix2latex
except ImportError:
    # Really ugly hack to please python3 import mechanisms
    import sys, os
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))

    sys.path.insert(0, SCRIPT_DIR)
    from matrix2latex import matrix2latex
    matrix2latex = matrix2latex.matrix2latex
    del sys.path[0]             # NOTE: ensure that matrix2latex does not change sys.path

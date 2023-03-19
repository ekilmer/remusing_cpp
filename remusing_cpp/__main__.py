"""
The `python -m remusing_cpp` entrypoint.
"""

import sys

from remusing_cpp._cli import main

sys.exit(main(sys.argv[1:]))

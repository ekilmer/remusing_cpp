"""
This module contains functionality for handling symbol names and namespace
mappings.
"""
from typing import Dict, List


def get_default_std_symbols() -> List[str]:
    """
    A hard-coded list of symbols that belong to the `std::` namespace.

    This should be used with caution as there may be overlap with first-party
    symbols of the same name.

    This list may also be incomplete.

    Collected with following script on the Ghidra decompiler C++ codebase:

    ```bash
    cd Ghidra/Features/Decompiler/src/decompile
    sed -nr 's/using std::(.*);/\1/p' **/* | sort | uniq
    ```

    Returns:
        A list of symbols belonging to the 'std::' namespace
    """
    # This is written in a way to more easily add/delete/sort the entries
    return """
abs
ceil
cerr
cin
cout
dec
endl
fabs
fixed
floor
forward_as_tuple
frexp
hex
ifstream
ios
ios_base
isnan
istream
istringstream
ldexp
list
log
make_pair
map
max
min
oct
ofstream
ostream
ostringstream
out_of_range
pair
piecewise_construct
round
regex
set
setfill
setprecision
setw
signbit
sqrt
string
to_string
unordered_map
vector
ws
""".strip().split(
        "\n"
    )


def get_default_symb_namespace_map() -> Dict[str, str]:
    """
    A hard-coded mapping of default unqualified symbol to namespace mapping.

    Returns:
        A default mapping from symbol name to namespace
    """
    return {s: "std" for s in get_default_std_symbols()}

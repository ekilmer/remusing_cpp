# RemUsing C++

This tool removes the `using` declarations and uses heuristics to automatically fix [unqualified C++ name](https://en.cppreference.com/w/cpp/language/unqualified_lookup) references with a corresponding namespace qualification, i.e. `string` to `std::string`.

## Background

This tool was built to more accurately (compared to `sed` or `perl`) automate the refactoring of [Ghidra's decompiler](https://github.com/NationalSecurityAgency/ghidra/tree/master/Ghidra/Features/Decompiler/src/decompile/cpp) to remove `using` declarations from the header after a [report](https://github.com/lifting-bits/sleigh/issues/139) of conflicting symbols.

Generally, in C++, [`using` declarations](https://en.cppreference.com/w/cpp/language/using_declaration) can pollute downstream consumers and [cause](https://stackoverflow.com/a/2880136) [issues](https://stackoverflow.com/a/6175850) that prevent compilation due to conflicting names. However, if a project has committed to this practice because they haven't yet encountered any issues internally, then it can be a time-consuming and manual task to refactor to a more correct representation without `using` declarations.

Currently, there exists only one tool (that I know of) that can perform a similar function to this tool: [clangd](https://clangd.llvm.org/). Clangd includes a [RemovingUsingNamespace](https://clang.llvm.org/extra/doxygen/RemoveUsingNamespace_8cpp_source.html) refactor that can fix `using namespace std;` and replace the relevant names with their qualified representation. However, this refactor-action does not work on header files, where this is most critically an issue. Moreover, `clangd` requires a working build of the project and will only refactor the code that is compiled, meaning that if you are compiling on Linux and there is conditional code for Windows compilation, then that code will be skipped during refactoring.

## Prerequisites

* Python 3.8+
* A C compiler (to build tree-sitter languages)

## Installation

After cloning this repo, this tool can be installed like any other Python package

```bash
python3 -m pip install .
```

This package is not on PyPI.

## Usage

The command-line entrypoint takes a single file to fix and prints the changes to stdout by default

```shell
remusing_cpp <file>
```

You can pass `-h` to read more about the usage and options.

For batch processing of many files, you can use [GNU Parallel](https://www.gnu.org/software/parallel/)

```shell
parallel -j 8 remusing_cpp -i ::: **/*.hh
```

### Docker

A Dockerfile is also provided to make installation easier:

```shell
docker build -t remusing_cpp .
```

And you can run it by sending data over standard input

```shell
docker run --rm -i remusing_cpp < test/data/test.cpp
```

or as a batch process in the current directory of a project

```shell
docker run --rm --volume "${PWD}:/workspace" remusing_cpp \
   /bin/bash -c 'parallel -j 8 remusing_cpp -i ::: **/*.hh'
```

## Implementation Notes

We use [tree-sitter](https://github.com/tree-sitter/tree-sitter) to parse the C++ source code. This is preferable because we see _all_ valid code, no matter if it's conditionally compiled, such as platform-specific code. Tree-sitter also doesn't require knowing how to build the project.

However, tree-sitter is not a compiler, so our heuristics for identifying relevant symbols/names and the transformation(s) are based on the concrete syntax tree and could potentially introduce compilation errors. The tool also relies on either manual specification of symbol name mapping to namespaces or can infer based on some using-declarations like `using std::string;` can be used to infer that any unqualified `string` type should be replaced with `std::string`.

If this tool prevents compilation, please open a bug report with the file that is causing issues. If possible, please reduce the file to a small representative example. The issue is likely that I have not thought about all C++ syntax constructs and need to encode a special case to fix the issue. Unfortunately, however, due to the limitations of tree-sitter, a good fix might not be possible and manual edits remain necessary.

## Known Bugs/Issues

Known bugs and issues should be tracked as a test in the [`test_known_bugs.py`](test/test_known_bugs.py) file.

1. Weird issue with finding the first `string` type in the following C++ declaration. Reported in issue [#192](https://github.com/tree-sitter/tree-sitter-cpp/issues/192) on tree-sitter C++ language repo. It is marked as `identifier` instead of `type_identifer`:

    ```c++
    map<string, vector<vector<string>>> t;
    ```

2. Unqualified names passed as arguments to a function (and most likely other cases like assignments) are not detected and fixed. This seems like a fundamental issue of tree-sitter not having more context. I think this would require C++ scoping information to detect whether a symbol name has been declared in the file or not.

   ```c++
   foo(cin);
   ```

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pydantic",
#     "tomlantic",
#     "tomlkit",
# ]
# ///

from enum import Enum
from typing import Final, Literal

from pydantic import BaseModel, Field
from tomlkit import loads

from tomlantic import ModelBoundTOML


class GrassplainTargetLanguageEnum(str, Enum):
    PYTHON = "python"


GrassplainTargetLanguageType = Literal[GrassplainTargetLanguageEnum.PYTHON]


class GCFMetaSection(BaseModel):
    description: str = ""
    max_line_length: int = 80
    min_description_padding: int = 12
    max_description_length: int = 25
    target_language: GrassplainTargetLanguageType = GrassplainTargetLanguageEnum.PYTHON
    extra: dict[str, str] = {}


class GrassplainArgument(BaseModel):
    description: str
    number_of_arguments: int = 1


class GrassplainOption(BaseModel):
    description: str
    delimiter: str = ""
    default: str = ""


class GrassplainFlag(BaseModel):
    description: str
    short: str = ""
    default: int = 0


class GCFGlobalSection(BaseModel):
    arguments: dict[str, GrassplainArgument] = {}
    options: dict[str, GrassplainOption] = {}
    flags: dict[str, GrassplainFlag] = {}


class GCFSubcommandSection(BaseModel):
    description: str
    arguments: dict[str, GrassplainArgument] = {}
    options: dict[str, GrassplainOption] = {}
    flags: dict[str, GrassplainFlag] = {}

    # god bless pydantic supporting cyclic references
    subcommands: dict[str, "GCFSubcommandSection"] = {}


class GrassplainConfigurationFile(BaseModel):
    meta: GCFMetaSection = GCFMetaSection()
    global_: GCFGlobalSection = Field(alias="global", default=GCFGlobalSection())
    subcommand: dict[str, GCFSubcommandSection] = {}


GRASSPLAIN_MEADOW_EXAMPLE: Final[str] = '''
# a 'real-world' example of the grassplain configuration file:
# see the end of the file for the help text output as reference

[meta]
# version of the program (optional)
description = "a docstring machine based on typing information"
# the maximum line length of the generated help text
# (defaults to 80 when unspecified)
max_line_length = 80
# the maximum number of characters the description of a subcommand/option should be padded to,
# starting from the start of the line
# (defaults to 12 when unspecified)
#
#            ↓
# ---------1111...
# 1234567890123...
#   XXXX      description
#
# (for an example of this, see the 'subcommands' section in the reference output)
min_description_padding = 12
# the maximum number of characters the description of a subcommand/option should be padded to,
# starting from the start of the line
# (defaults to 25 when unspecified)
#
#                        ↓
# ---------1111111111222222
# 1234567890123456789012456...
#   XXXXXXXXXXXXXX  description
#   YYYYYYY         description
#   ZZZZZZZZZZZZZZZZZZZZZZZZ
#                   description
#
# (for an example of this, see the 'global options' section in the reference output)
max_description_padding = 25
target_language = "python"

# extra text to be appended to the end of the help message
[meta.extra]
# leading and trailing whitespaces/newlines are stripped, and newlines between the string are
# preserved. grassplain will NOT enforce line length on the body of the extra info, so it's up to
# you to format it properly!
"additional information" = """
similar behaviour for ignoring files, docstrings, outdated docstrings, and
malformed docstrings can be done using a top-level '# meadow: ignore' comment

top-level, per-file:
  equivalent to '--ignore'
per-function or per-class:
  equivalent to '--ignore-no-docstring', '--ignore-outdated', and
  '--ignore-malformed' (the comment within the body definition as a comment
  with a standalone line)

  example: (choose one)
      def foo():
          # meadow: ignore
          pass
     note that in-defintion comments must be 'standalone', meaning there is no
     other text on the line
"""

# options are shown in the order they are defined in the configuration file
[global.arguments.file]
# defaults to '1' if not specified,
# could also be set to -1 for unlimited arguments (will be a list)
number_of_arguments = -1
description         = "a list of files or globs to target for processing"

[global.options.ignore]
short       = "i"  # specify a one-character shortened form of the option, if desired
description = "a comma-separated list of globs to ignore when processing files"
delimiter   = ","  # specify a custom delimiter for the option, if desired

[global.flags.ignore-no-docstring]
short       = "n"
description = "whether to ignore functions and classes with no docstrings"
# remember! flags are treated as integers! you could put true/false here if you want to,
# but the resulting value will be 1/0 respectively.
default     = 0

[global.flags.ignore-outdated]
short = "o"
description = "whether to ignore functions and classes with outdated docstrings"

[global.flags.ignore-malformed]
short = "m"
description = "whether to ignore functions and classes with malformed docstrings"

[subcommand.generate]
description = """if passed as the first argument, meadow will generate docstrings templates and \
                 write the result to disk. else, meadow will lint the docstrings of the files and \
                 output any issues found"""

# depending on the complexity of the subcommand, you may or may not want to show the subcommands'
# positional arguments and options in the top-level help text. (the one that shows when you run the
# 'help' subcommand)
# however, using 'help <subcommand>' will always show the subcommand's positional arguments and
# options.
# here, we choose to show the details of the 'generate' subcommand because it has a few options
# and there aren't that many subcommands/options within the 'meadow' program.
# (defaults to 'false' when unspecified)
show_details = true

[subcommand.generate.options.custom-message]
description = """specifies a custom message for when newly generated docstring segments are to be \
                 replaced by the user"""

[subcommand.generate.flags.fix-malformed]
description = "whether to generate a fix for malformed docstrings"

# usage: meadow {generate} [--custom-message MESSAGE]] [-h] [-v] [-i IGNORE] [-n]
#          [-o] [-m] [FILE, ...]
#
# a docstring machine based on typing information
#
# positional arguments:
#   FILE      a list of files to process
#
# subcommands:
#   generate  if passed as the first argument, meadow will generate docstrings
#               templates and write the result to disk.
#               else, meadow will lint the docstrings of the files and output any
#               issues found
#
# 'generate' subcommand options:
#   --custom-message MESSAGE  specifies a custom message for when newly generated
#                               docstring segments are to be replaced by the user
#   --fix-malformed           whether to generate a fix for malformed docstrings
#
# global options:
#   -h, --help           show this help message and exit
#   -v, --version        show program's version number and exit
#   -i, --ignore IGNORE  a comma-separated list of globs to ignore when processing
#                          files
#   -n, --ignore-no-docstring
#                        whether to ignore functions and classes with no
#                          docstrings
#   -o, --ignore-outdated
#                        whether to ignore functions and classes with outdated
#                          docstrings
#   -m, --ignore-malformed
#                        whether to ignore functions and classes with malformed
#                          docstrings
#
# additional information:
#   similar behaviour for ignoring files, docstrings, outdated docstrings, and
#   malformed docstrings can be done using a top-level '# meadow: ignore' comment
#
#   top-level, per-file:
#     equivalent to '--ignore'
#   per-function or per-class:
#     equivalent to '--ignore-no-docstring', '--ignore-outdated', and
#     '--ignore-malformed' (the comment within the body definition as a comment
#     with a standalone line)
#
#     example: (choose one)
#         def foo():
#             # meadow: ignore
#             pass
#        note that in-defintion comments must be 'standalone', meaning there is no
#        other text on the line
'''


def test():
    ModelBoundTOML(GrassplainConfigurationFile, loads(GRASSPLAIN_MEADOW_EXAMPLE))


if __name__ == "__main__":
    test()

# tomlantic

> [!WARNING]  
> tomlantic is at 0.2.1 and currently, only i use it myself. it isn't battle tested,
> so issues may arise.  
> if you're willing to run into potential bugs and issues, feel free to use it!

marrying [pydantic](https://github.com/pydantic/pydantic) models and
[tomlkit](https://github.com/sdispater/tomlkit) documents for data validated,
style-preserving toml files

uses generics to automagically preserve model types, so you don't lose out on model type
information :D

- [usage](#usage)
  - [installation](#installation)
  - [quickstart](#quickstart)
  - [validators](#validators)
- [api reference](#api-reference)
- [licence](#licence)

## usage

### installation

there are three notable methods to use tomlantic with your project:

1. install from pypi

   ```shell
   pip install tomlantic
   ```

2. install from source

   ```shell
   pip install git+https://github.com/markjoshwel/tomlantic
   ```

3. directly include tomlantic.py in your project

   ```shell
   wget https://raw.githubusercontent.com/markjoshwel/tomlantic/main/tomlantic/tomlantic.py
   ```

   tomlantic is a single file module and is free and unencumbered software released
   into the public domain. so, use it however you please!  
   see the [licence](#licence) section for more information.

### quickstart

```python
import pydantic
import tomlkit

from tomlantic import ModelBoundTOML


class Project(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)
    name: str
    description: str
    typechecked: bool


class File(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)
    project: Project


toml_doc = tomlkit.parse(
    "[project]\n"
    'name = "tomlantic"\n'
    'description = "marrying pydantic models and tomlkit documents"\n'
    "typechecked = false\n"
)

# where tomlantic comes in handy
toml = ModelBoundTOML(File, toml_doc)

# access the model with .model and change the model freely
model: File = toml.model
model.project.typechecked = True

# dump the model back to a toml document
new_toml_doc = toml.model_dump_toml()
assert new_toml_doc["project"]["typechecked"] == True  # type: ignore
print(new_toml_doc.as_string())
```

### validators

tomlantic also comes with a neat set of validators to use with handling pydantic model
fields and/or the toml document itself:

- [tomlantic.validate_to_specific_type](#def-tomlanticvalidate_to_specific_type)
- [tomlantic.validate_to_multiple_types](#def-tomlanticvalidate_to_multiple_types)
- [tomlantic.validate_homogeneous_collection](#def-tomlanticvalidate_homogeneous_collection)
- [tomlantic.validate_heterogeneous_collection](#def-tomlanticvalidate_heterogeneous_collection)

## api reference

- [tomlantic.ModelBoundTOML](#class-tomlanticmodelboundtoml)
  - [model_dump_toml](#def-tomlanticmodelboundtomlmodel_dump_toml)
  - [get_field](#def-tomlanticmodelboundtomlget_field)
  - [set_field](#def-tomlanticmodelboundtomlset_field)
  - [difference_between_document](#def-tomlanticmodelboundtomldifference_between_document)
  - [load_from_document](#def-tomlanticmodelboundtomlload_from_document)
- [tomlantic.Difference](#class-tomlanticdifference)
- [tomlantic.get_toml_field](#def-tomlanticget_toml_field)
- [tomlantic.set_toml_field](#def-tomlanticset_toml_field)
- [tomlantic.TomlanticException](#class-tomlantictomlanticexception)
- [tomlantic.TOMLBaseSingleError](#class-tomlantictomlbasesingleerror)
- [tomlantic.TOMLAttributeError](#class-tomlantictomlattributeerror)
- [tomlantic.TOMLFrozenError](#class-tomlantictomlfrozenerror)
- [tomlantic.TOMLMissingError](#class-tomlantictomlmissingerror)
- [tomlantic.TOMLValueError](#class-tomlantictomlvalueerror)
- [tomlantic.TOMLValidationError](#class-tomlantictomlvalidationerror)
- [tomlantic.validate_to_specific_type](#def-tomlanticvalidate_to_specific_type)
- [tomlantic.validate_to_multiple_types](#def-tomlanticvalidate_to_multiple_types)
- [tomlantic.validate_homogeneous_collection](#def-tomlanticvalidate_homogeneous_collection)
- [tomlantic.validate_heterogeneous_collection](#def-tomlanticvalidate_heterogeneous_collection)

### class tomlantic.ModelBoundTOML

tomlantic's magical glue class for pydantic models and tomlkit documents

will handle pydantic.ValidationErrors into more toml-friendly error messages.  
set `handle_errors` to `False` to raise the original
[`pydantic.ValidationError`](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ValidationError)

- attributes:
  - model: [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel)

- initialisation arguments:
  - model: [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel)
  - toml: [`tomlkit.TOMLDocument`](https://tomlkit.readthedocs.io/en/latest/api/#module-tomlkit.toml_document)
  - human_errors: `bool` = `False`

- raises:
  - [`tomlantic.TOMLValidationError`](#class-tomlantictomlvalidationerror)  
    if the document does not validate with the model
  - [`pydantic.ValidationError`](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ValidationError)  
    if the document does not validate with the model and `handle_errors` is `False`

- methods:
  - [model_dump_toml()](#def-tomlanticmodelboundtomlmodel_dump_toml)

- usage:

  ```python
  # instantiate the class
  toml = ModelBoundTOML(YourModel, tomlkit.parse(...))
  # access your model with .model
  toml.model.message = "blowy red vixens fight for a quick jump"
  # dump the model back to a toml document
  toml_document = toml.model_dump_toml()
  # or to a toml string
  toml_string = toml.model_dump_toml().as_string()
  ```

### def tomlantic.ModelBoundTOML.model_dump_toml()

method that dumps the model as a style-preserved `tomlkit.TOMLDocument`

- signature:

  ```python
  def model_dump_toml(self) -> TOMLDocument:
  ```

- returns [`tomlkit.TOMLDocument`](https://tomlkit.readthedocs.io/en/latest/api/#module-tomlkit.toml_document)

### def tomlantic.ModelBoundTOML.get_field()

safely retrieve a field by it's location. not recommended for general use due to
a lack of type information, but useful when accessing fields programatically

- signature:

  ```python
  def get_field(
      self,
      location: Union[str, Tuple[str, ...]],
      default: Any = None,
  ) -> Any: ...
  ```

- arguments:
  - location: `Union[str, Tuple[str, ...]]`
  - default: `Any` = `None`

- returns the field if it exists, otherwise `default`

### def tomlantic.ModelBoundTOML.set_field()

sets a field by it's location. not recommended for general use due to a lack of
type safety, but useful when setting fields programatically

will handle `pydantic.ValidationError` into more toml-friendly error messages.
set `handle_errors` to `False` to raise the original `pydantic.ValidationError`

- signature:

  ```python
  def set_field(
      self,
      location: Union[str, Tuple[str, ...]],
      value: Any,
      handle_errors: bool = True,
  ) -> None: ...
  ```

- arguments:
  - location:      `Union[str, Tuple[str, ...]]`
  - value:         `Any`
  - handle_errors: `bool` = True

- raises:
  - `AttributeError` if the field does not exist
  - [`tomlantic.TOMLValidationError`](#class-tomlantictomlvalidationerror) if the document does not validate with the model
  - [`pydantic.ValidationError`](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ValidationError) if the document does not validate with the model and `handle_errors` is `False`

### def tomlantic.ModelBoundTOML.difference_between_document()

returns a tomlantic.Difference object of the incoming and outgoing fields that
were changed between the model and the comparison_document

- signature:

  ```python
  def difference_between_document(
      self,
      incoming_document: TOMLDocument
  ) -> Difference: ...
  ```

- arguments:
  - incoming_document: [`tomlkit.TOMLDocument`](https://tomlkit.readthedocs.io/en/latest/api/#module-tomlkit.toml_document)

- returns [`tomlantic.Difference`](#class-tomlanticdifference)

### def tomlantic.ModelBoundTOML.load_from_document()

override fields with those from a new document

by default, this method selectively overrides fields. so fields that have been
changed in the model will NOT be overriden by the incoming document

pass `False` to the `selective` argument to override ALL fields in the model with
the fields of the incoming document

no changes are applied until the incoming document passes all model validations

- signature:

  ```python
  def load_from_document(
      self,
      incoming_document: TOMLDocument,
      selective: bool = True,
  ) -> None:
  ```

- arguments:
  - incoming_document: [`tomlkit.TOMLDocument`](https://tomlkit.readthedocs.io/en/latest/api/#module-tomlkit.toml_document)
  - selective: `bool` = `False`

### class tomlantic.Difference

a named tuple for the differences between an outgoing tomlantic.ModelBoundTOML and a
tomlkit.TOMLDocument

- signature:

  ```python
  class Difference(NamedTuple): ...
  ```

- attributes:
  - incoming_changed_fields: `Tuple[str, ...]`
  - outgoing_changed_fields: `Tuple[str, ...]`

### def tomlantic.get_toml_field()

safely retrieve a field by it's location. not recommended for general use due to
a lack of type information, but useful when accessing fields programatically

- signature:

  ```python
  def get_toml_field(
      document: TOMLDocument,
      location: Union[str, Tuple[str, ...]],
      default: Any = None,
  ) -> Any:
  ```

- arguments:
  - document: `TOMLDocument`
  - location: `Union[str, Tuple[str, ...]]`
  - default: `Any` = `None`

- returns the field if it exists, otherwise `default`

### def tomlantic.set_toml_field()

safely retrieve a toml documents field by it's location. not recommended for general
use due to a lack of type information, but useful when accessing fields programatically

raises `KeyError` if the field does not exist, or a `LookupError` if attempting to
set a field in a non-table

if handling for errors, handle `KeyError` before `LookupError` as `LookupError` is
the base class for `KeyError`

- signature:
  
  ```python
  def set_toml_field(
      document: TOMLDocument,
      location: Union[str, Tuple[str, ...]],
      value: Any,
  ) -> None:
  ```

- arguments: 
  - document: `TOMLDocument`
  - location: `Union[str, Tuple[str, ...]]`
  - value: `Any`

### class tomlantic.TomlanticException

base exception class for all tomlantic errors

- signature:

  ```python
  class TomlanticException(Exception): ...
  ```

the hierarchy of exceptions that inherit this class are:

```text
TomlanticException
├── TOMLValidationError
└── TOMLBaseSingleError
    ├── TOMLAttributeError
    ├── TOMLFrozenError
    ├── TOMLMissingError
    ├── TOMLValueError
    └── TOMLValidationError
```

### class tomlantic.TOMLBaseSingleError

base exception class for single errors, e.g. TOMLMissingError, TOMLValueError

inherits [TomlanticException](#class-tomlantictomlanticexception)

base exception class for all tomlantic errors

- signature:

  ```python
  class TOMLBaseSingleError(TomlanticException): ...
  ```

- attributes:
  - loc: `Tuple[str, ...]`  
    the location of the error in the toml document  
    example: `('settings', 'name') = settings.name`

  - msg: `str`  
    the error 'message' (if any)

  - pydantic_error: [`pydantic_core.ErrorDetails`](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ErrorDetails)  
    the original pydantic error, this is what you see in the list of errors when you
    handle a [`pydantic.ValidationError`](https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ValidationError)

### class tomlantic.TOMLAttributeError

error raised when an field does not exist, or is an extra field not in the model and the
model has forbidden extra fields

inherits [TOMLBaseSingleError](#class-tomlantictomlbasesingleerror),
go there for attributes

- signature:

  ```python
  class TOMLAttributeError(TOMLBaseSingleError): ...
  ```

### class tomlantic.TOMLFrozenError

error raised when assigning a value to a frozen field or value

inherits [TOMLBaseSingleError](#class-tomlantictomlbasesingleerror),
go there for attributes

- signature:

  ```python
  class TOMLFrozenError(TOMLBaseSingleError): ...
  ```

### class tomlantic.TOMLMissingError

raised when a toml document does not contain all the required fields/tables of a model

inherits [TOMLBaseSingleError](#class-tomlantictomlanticexception),
go there for attributes

- signature:

  ```python
  class TOMLMissingError(TOMLBaseSingleError): ...
  ```

### class tomlantic.TOMLValueError

raised when an item in a toml document is invalid for its respective model field

inherits [TOMLBaseSingleError](#class-tomlantictomlanticexception),
go there for attributes

- signature:

  ```python
  class TOMLValueError(TOMLBaseSingleError): ...
  ```

### class tomlantic.TOMLValidationError

a toml-friendly version of pydantic.ValidationError, raised when instantiating
[tomlantic.ModelBoundTOML](#class-tomlanticmodelboundtoml)

inherits [TomlanticException](#class-tomlantictomlanticexception)

- signature:

  ```python
  class TOMLValidationError(TomlanticException): ...
  ```

- attributes:
  - errors: `Tuple[TOMLBaseSingleError, ...]`  
    all validation errors raised when validating the toml document with the model

### def tomlantic.validate_to_specific_type()

validate a value's type to be a specific type

- signature:

  ```python
  def validate_to_specific_type(v: Any, t: Type[T]) -> T: ...
  ```

- usage:

  ```python
  validate_to_specific_type("hello", str)  # returns "hello"
  validate_to_specific_type(42, str)       # raises ValueError
  ```

### def tomlantic.validate_to_multiple_types()

validate a value's type to be in a tuple of specific types

- signature:

  ```python
  def validate_to_multiple_types(v: Any, t: Tuple[Type[Ts], ...]) -> Ts:
  ```

- usage:

  ```python
  validate_to_multiple_types("hello", (str, int))  # returns "hello"
  validate_to_multiple_types(42, (str, int))       # returns 42
  validate_to_multiple_types(42.0, (str, int))     # raises ValueError
  ```

### def tomlantic.validate_homogeneous_collection()

validate values of a collection to a specific type

- signature:

  ```python
  def validate_homogeneous_collection(v: Any, t: Type[T]) -> Collection[T]:
  ```

- usage:

  ```python
  validate_homogeneous_collection([1, 2, 3], int)    # returns [1, 2, 3]
  validate_homogeneous_collection([1, 2, "3"], int)  # raises ValueError
  ```

### def tomlantic.validate_heterogeneous_collection()

validate values of a collection to a specific type or a tuple of types

- signature:

  ```python
  def validate_heterogeneous_collection(v: Collection[Any], t: Tuple[Type[Ts], ...]) -> Collection[Ts]: ...
  ```

- usage:

  ```python
  validate_heterogeneous_collection([1, 2, "3"], (int, str))    # returns [1, 2, "3"]
  validate_heterogeneous_collection([1, 2, "3"], (int, float))  # raises ValueError
  ```

## licence

tomlantic is free and unencumbered software released into the public domain. for more
information, please refer to [UNLICENCE](/UNLICENCE), <https://unlicense.org>, or the
python module docstring.

```text
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
```

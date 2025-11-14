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

![hits](https://img.shields.io/endpoint?url=https://hits.dwyl.com/markjoshwel/tomlantic.json&style=flat-square&label=hits&color=6244bb)

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
   wget https://raw.githubusercontent.com/markjoshwel/tomlantic/refs/tags/v0.2.1/tomlantic/tomlantic.py
   ```

   tomlantic is a single file module and is dually licenced for public domain
   dedication, or a public domain-equivalent licence. so, use it however you please!  
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
    "typechecked = false  # change this!\n"
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
# ^^ [project]
#    name = "tomlantic"
#    description = "marrying pydantic models and tomlkit documents"
#    typechecked = true  # change this!
```

## api reference

> [!IMPORTANT]  
> 0.2.2 is currently in development.
> please see documentation as during the [0.2.1 branch](https://github.com/markjoshwel/tomlantic/tree/v0.2.1) for more information.

TODO

## licence

tomlantic is dually licensed under the [Unlicense](https://unlicense.org/)
and the [0BSD License](https://opensource.org/licenses/0BSD).

for more information, please refer to [LICENCING](/LICENCING).

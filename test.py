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

# where tomlantic becomes handy
toml = ModelBoundTOML(File, toml_doc)

# access the model with .model and change the model freely
model: File = toml.model
model.project.typechecked = True

# dump the model back to a toml document
new_toml_doc = toml.model_dump_toml()
assert new_toml_doc["project"]["typechecked"] == True  # type: ignore
print(new_toml_doc.as_string())

import pydantic
import tomlkit

import tomlantic


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

# 0.1.0: validators
tomlantic.validate_heterogeneous_collection([1, 2, "3"], (int, str))
tomlantic.validate_homogeneous_collection([1, 2, 3], int)
tomlantic.validate_to_multiple_types("3", (int, str))
tomlantic.validate_to_specific_type("3", str)

# 0.1.0: ModelBoundTOML
toml = tomlantic.ModelBoundTOML(File, toml_doc)
print(toml, "\n")

model: File = toml.model
model.project.typechecked = True

# new in 0.2.0: test ModelBoundTOML.get_field and ModelBoundTOML.set_field
assert toml.get_field("project.typechecked") == True

toml.set_field("project.typechecked", False)
assert toml.model.project.typechecked == False
toml.set_field("project.typechecked", True)

# new in 0.2.0: test differences
diff_test_empty = tomlkit.parse("\n")
diff = toml.difference_between_document(incoming_document=diff_test_empty)
assert diff == tomlantic.Difference(
    incoming_changed_fields=(),
    outgoing_changed_fields=(("project"),),
)
print(diff, "\n")

diff_test_changed = tomlkit.parse(
    "[project]\n" 'name = "NOT tomlantic"\n' "typechecked = true\n"
)
diff = toml.difference_between_document(incoming_document=diff_test_changed)
print(diff, "\n")
assert diff == tomlantic.Difference(
    incoming_changed_fields=("project.name",),
    outgoing_changed_fields=("project.name", "project.description"),
)

# new in 0.2.0: test get_toml_field and set_toml_field
print(tomlantic.get_toml_field(document=toml_doc, location="project.name"), "\n")
tomlantic.set_toml_field(
    document=toml_doc, location="project.name", value="NOT tomlantic"
)
assert toml_doc["project"]["name"] == "NOT tomlantic"  # type: ignore

try:
    tomlantic.set_toml_field(
        document=toml_doc, location="project.name.nonexistent", value="?"
    )
except:
    pass
else:
    assert "set_toml_field should have failed here"

# new in 0.2.0:

# 0.1.0: dump the model back to a toml document
new_toml_doc = toml.model_dump_toml()
assert new_toml_doc["project"]["typechecked"] == True  # type: ignore
print(new_toml_doc.as_string())

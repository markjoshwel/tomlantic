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

model: File = toml.model
model.project.typechecked = True

# 0.1.0: dump the model back to a toml document
new_toml_doc = toml.model_dump_toml()
assert new_toml_doc["project"]["typechecked"] is True  # type: ignore

# new in 0.2.0: test ModelBoundTOML.get_field and ModelBoundTOML.set_field
assert toml.get_field("project.typechecked") is True

toml.set_field("project.typechecked", False)
assert toml.model.project.typechecked is False
toml.set_field("project.typechecked", True)

# new in 0.2.0: test differences
toml = tomlantic.ModelBoundTOML(File, toml_doc)
diff_test_empty = tomlkit.parse("\n")
diff = toml.difference_between_document(incoming_document=diff_test_empty)
assert diff == tomlantic.Difference(
    incoming_changed_fields=(),
    outgoing_changed_fields=(("project",)),
)

toml = tomlantic.ModelBoundTOML(File, toml_doc)
diff_test_changed = tomlkit.parse(
    '[project]\nname = "NOT tomlantic"\ntypechecked = true\n'
)
diff = toml.difference_between_document(incoming_document=diff_test_changed)
assert diff == tomlantic.Difference(
    incoming_changed_fields=(
        "project.name",
        "project.typechecked",
    ),
    outgoing_changed_fields=("project.description",),
)

# new in 0.2.0: test get_toml_field and set_toml_field
toml = tomlantic.ModelBoundTOML(File, toml_doc)
assert (
    tomlantic.get_toml_field(document=toml_doc, location="project.name") == "tomlantic"
)
tomlantic.set_toml_field(
    document=toml_doc, location="project.name", value="NOT tomlantic"
)
assert toml_doc["project"]["name"] == "NOT tomlantic"  # type: ignore

try:
    tomlantic.set_toml_field(
        document=toml_doc,
        location="project.name.nonexistent",
        value="?",
    )
except Exception:
    pass
else:
    assert "set_toml_field should have failed here"

# new in 0.2.0: ModelBoundTOML.load_from_document
toml = tomlantic.ModelBoundTOML(File, toml_doc)
toml.model.project.typechecked = True
incoming_toml_doc = tomlkit.parse(
    "[project]\n"
    'name = "tomlantic"\n'
    'description = "marrying pydantic models and tomlkit documents!"\n'
    "typechecked = '???'\n"
    "whuh = '???'\n"
)
toml.load_from_document(incoming_document=incoming_toml_doc, selective=True)
assert toml.model.project.description.endswith("!")
assert toml.get_field("project.whuh") is None, "extra fields were not ignored"

print("ok!")

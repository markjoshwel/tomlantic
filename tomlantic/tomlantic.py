"""
tomlantic: marrying pydantic models and tomlkit documents
---------------------------------------------------------
with all my heart, 2024, mark joshwel <mark@joshwel.co>

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
"""

from copy import deepcopy
from typing import Any, Collection, Generic, List, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails
from tomlkit import TOMLDocument
from tomlkit import items as tomlitems
from tomlkit import table

T = TypeVar("T")
Ts = TypeVar("Ts")


def validate_to_specific_type(v: Any, t: Type[T]) -> T:
    """
    validate a value's type to be a specific type

    usage:
        ```py
        validate_to_specific_type("hello", str)  # returns "hello"
        validate_to_specific_type(42, str)       # raises ValueError
        ```
    """

    if not isinstance(v, t):
        raise ValueError(
            f"value of type '{v.__class__.__name__}' must be a '{t.__name__}'"
        )

    return v


def validate_to_multiple_types(v: Any, t: Tuple[Type[Ts], ...]) -> Ts:
    """
    validate a value's type to be in a tuple of specific types

    usage:
        ```py
        validate_to_multiple_types("hello", (str, int))  # returns "hello"
        validate_to_multiple_types(42, (str, int))       # returns 42
        validate_to_multiple_types(42.0, (str, int))     # raises ValueError
        ```

    returns `v` or raises `ValueError` if `v` is not of type `t`
    """

    if not isinstance(v, t):
        raise ValueError(
            f"value of type '{v.__class__.__name__}' must be of one of types "
            "(" + ", ".join([f"'{_t.__name__}'" for _t in t]) + ")"
        )

    return v


def validate_homogeneous_collection(v: Any, t: Type[T]) -> Collection[T]:
    """
    validate values of a collection to a specific type

    usage:
        ```py
        validate_homogeneous_collection([1, 2, 3], int)    # returns [1, 2, 3]
        validate_homogeneous_collection([1, 2, "3"], int)  # raises ValueError
        ```

    returns `v` or raises `ValueError` if any value in `v` is not of type `t`
    """

    if not isinstance(v, Collection):
        raise ValueError("value must be a collection (list, tuple, set, etc)")

    for idx, _v in enumerate(v, start=1):
        if not isinstance(_v, t):
            raise ValueError(
                f"value {idx} ('{_v}') in collection of type "
                f"'{_v.__class__.__name__}' must be of type '{t.__name__}'"
            )

    return v


def validate_heterogeneous_collection(
    v: Collection[Any], t: Tuple[Type[Ts], ...]
) -> Collection[Ts]:
    """
    validate values of a collection to a specific type or a tuple of types

    usage:
        ```py
        validate_heterogeneous_collection([1, 2, "3"], (int, str))    # returns [1, 2, "3"]
        validate_heterogeneous_collection([1, 2, "3"], (int, float))  # raises ValueError
        ```
    """

    if not isinstance(v, Collection):
        raise ValueError("value must be a collection (list, tuple, set, etc)")

    for idx, _v in enumerate(v, start=1):
        if not isinstance(_v, t):
            raise ValueError(
                f"value {idx} ('{_v}') in collection of type '{_v.__class__.__name__}' "
                f"must one of types "
                "(" + ", ".join([f"'{_t.__name__}'" for _t in t]) + ")"
            )

    return v


class TomlanticException(Exception):
    """base exception class for all tomlantic errors"""

    pass


class TOMLBaseSingleError(TomlanticException):
    """base exception class for single errors, e.g. TOMLMissingError, TOMLValueError"""

    loc: Tuple[str, ...]
    pydantic_error: ErrorDetails

    def __init__(
        self,
        *args,
        loc: Tuple[str, ...],
        pydantic_error: ErrorDetails,
    ) -> None:
        self.loc = loc
        self.pydantic_error = pydantic_error
        super().__init__(*args)


class TOMLMissingError(TOMLBaseSingleError):
    """error raised when a toml document does not contain all the required fields/tables of a model"""

    pass


class TOMLValueError(TOMLBaseSingleError):
    """error raised when an item in a toml document is invalid for its respective model field"""

    pass


class TOMLFrozenError(TOMLBaseSingleError):
    """error raised when assigning a value to a frozen field or value"""

    pass


class TOMLAttributeError(TOMLBaseSingleError):
    """
    error raised when an field does not exist, or is an extra field not in the model and
    the model has forbidden extra fields
    """

    pass


class TOMLValidationError(TomlanticException):
    """
    a toml-friendly version of pydantic.ValidationError,
    raised when instantiating ModelBoundTOML
    """

    errors: Tuple[TOMLBaseSingleError, ...]

    def __init__(
        self,
        *args,
        errors: Tuple[TOMLBaseSingleError, ...],
    ) -> None:
        self.errors = errors
        super().__init__(*args)


M = TypeVar("M", bound=BaseModel)


class ModelBoundTOML(Generic[M]):
    """
    glue class for pydantic models and tomlkit documents

    attributes:
      - model: BaseModel

    usage:
        ```py
        # instantiate the class
        toml = ModelBoundTOML(YourModel, tomlkit.parse(...))
        # access your model with ModelBoundTOML.model
        toml.model.message = "blowy red vixens fight for a quick jump"
        # dump the model back to a toml document
        toml_document = toml.model_dump_toml()
        # or to a toml string
        toml_string = toml.model_dump_toml().as_string()
        ```
    """

    model: M
    __original_model: M
    __document: TOMLDocument

    def __init__(
        self,
        model: Type[M],
        document: TOMLDocument,
        handle_errors: bool = True,
    ) -> None:
        """instantiates the class with a `BaseModel` and a `TOMLDocument`

        will handle pydantic.ValidationErrors into more toml-friendly error messages.
        set `handle_errors` to `False` to raise the original pydantic.ValidationError

        arguments:
          - model:         `pydantic.BaseModel`
          - document:      `tomlkit.toml_document.TOMLDocument`
          - handle_errors: `bool` = False

        raises:
          - `tomlantic.TOMLMissingError` if the document does not contain all the required fields/tables of the model
          - `tomlantic.TOMLValueError`   if an item in the document is invalid for its respective model field
          - `pydantic.ValidationError`   if the document does not validate with the model
        """
        try:
            self.model = model.model_validate(document)

        except ValidationError as e:
            if not handle_errors:
                raise e

            # TODO: check each validation error and classify them to value errors or
            #       other types of errors
            #       https://docs.pydantic.dev/dev/errors/validation_errors/
            #
            # special cases:
            #   missing -> tomlantic.TOMLMissingError
            #
            # everything else -> tomlantic.TOMLValueError

            errors: List[TOMLBaseSingleError] = []

            error_messages: List[str] = []

            for pydantic_error in e.errors():
                loc: Tuple[str, ...] = ("unknown",)

                try:
                    loc = tuple(
                        validate_homogeneous_collection(pydantic_error["loc"], str)
                    )

                except Exception:
                    pass

                if pydantic_error["type"] is None:
                    continue

                elif pydantic_error["type"] == "missing":
                    errors.append(
                        TOMLMissingError(
                            str(
                                pydantic_error.get(
                                    "msg",
                                    "the required field is missing from the document",
                                )
                            ),
                            loc=loc,
                            pydantic_error=pydantic_error,
                        )
                    )

                elif pydantic_error["type"] in ("frozen_field", "frozen_instance"):
                    errors.append(
                        TOMLFrozenError(
                            str(
                                pydantic_error.get(
                                    "msg",
                                    "attempting to override a field that is frozen or an instance that is frozen",
                                )
                            ),
                            loc=loc,
                            pydantic_error=pydantic_error,
                        )
                    )

                elif pydantic_error["type"] in ("no_such_attribute", "extra_forbidden"):
                    errors.append(
                        TOMLAttributeError(
                            str(
                                pydantic_error.get(
                                    "msg",
                                    "the field does not exist or is an extra field not in the model",
                                )
                            ),
                            loc=loc,
                            pydantic_error=pydantic_error,
                        )
                    )

                else:
                    errors.append(
                        TOMLValueError(
                            str(pydantic_error.get("msg", "unknown value error")),
                            loc=loc,
                            pydantic_error=pydantic_error,
                        )
                    )

            for tomalntic_error in errors:
                error_messages.append(
                    f'Field "{".".join(tomalntic_error.loc)}": {str(tomalntic_error)} '
                    f'({tomalntic_error.pydantic_error["type"]})'
                )

            raise TOMLValidationError(
                f"{len(errors)} {'error' if len(errors) == 1 else 'errors'} "
                "occurred while validating the TOML document:\n"
                + "\n".join([f"  {e}" for e in error_messages]),
                errors=tuple(errors),
            )

        self.__original_model = model.model_validate(
            document
        )  # if we pass the first validation, this should pass too
        self.__document = document

    def model_dump_toml(self) -> TOMLDocument:
        """dumps the model as a style-preserved `tomlkit.toml_document.TOMLDocument`"""
        document = deepcopy(self.__document)

        # add values that were changed from when the model was instantiated
        def apply_model_differences(
            original_model: BaseModel,
            current_model: BaseModel,
            toml: Union[TOMLDocument, tomlitems.Table],
        ) -> None:
            for original_kv, current_kv in zip(original_model, current_model):
                og_key, og_val = original_kv
                cu_key, cu_val = current_kv

                assert (
                    og_key == cu_key
                ), f"old model and new model has different keys: '{og_key}'/'{cu_key}' (unreachable?)"

                if isinstance(cu_val, BaseModel):
                    assert isinstance(
                        og_val, BaseModel
                    ), f"key '{og_key}'/'{cu_key}' old model and new model arent basemodels (unreachable?)"

                    # check if table exists
                    if cu_key not in toml:
                        toml[cu_key] = table()

                    toml_cu_key = toml[cu_key]
                    assert isinstance(
                        toml_cu_key, (TOMLDocument, tomlitems.Table)
                    ), f"key {cu_key}: attempting to recurse into an non-table/document"

                    apply_model_differences(og_val, cu_val, toml_cu_key)

                elif original_kv != current_kv:
                    cu_key, cu_val = current_kv
                    toml[cu_key] = cu_val

        apply_model_differences(self.__original_model, self.model, document)
        return document

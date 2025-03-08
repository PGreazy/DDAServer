from ninja import Schema
from pydantic.alias_generators import to_camel


class BaseSchema(Schema):
    """
    A small base class that defines basic, global behavior that
    any response object should follow. All objects involved in
    responses should inherit this config. Descriptions of these
    attributes can be found at:
    https://docs.pydantic.dev/2.10/api/config/#pydantic.config.ConfigDict
    """
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "use_enum_values": True,
        "validate_assignment": True
    }

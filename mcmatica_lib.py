from dataclasses import dataclass, field, asdict
import typing
from email.policy import default
from enum import Enum


class InputTypeEnum(str, Enum):
    TEXT = 'text',
    NUMBER = 'number',
    CHECKBOX = 'checkbox',
    SELBOX = 'selbox',
    EMAIL = 'email',
    PASSWORD ='password',
    DATE = 'date'
    DATETIME = 'datetime'


def empty_list():
    return []

@dataclass(init=True, slots=True, frozen=False)
class McSqlModelInfo:
    label: str
    input_type: InputTypeEnum = field(default=InputTypeEnum.TEXT)
    sel_list: typing.List[any] = field(default_factory=empty_list)
    in_grid: bool = field(default=True)
    in_form: bool = field(default=True)
    editable: bool = field(default=True)
    required: bool = field(default=False)
    width: str = field(default="100%")
    form_bloc_name: str = field(default=None)
    def dict(self):
        #return dict(json_schema_extra={k: str(v) for k, v in asdict(self).items()})
        return dict(json_schema_extra=self)

    def build_selection_list(self, selection_list: typing.List[any]) -> object:
        self.sel_list = selection_list
        return self

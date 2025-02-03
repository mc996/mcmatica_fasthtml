from dataclasses import dataclass
import dataclasses
import typing
from enum import Enum
from typing import Generic, Literal, overload

#T = typing.TypeVar("T")

class McFieldsSetType(Enum):
    BLOC = "BLOC"
    GRID = "GRID"

class McFieldVisibilityType(Enum):
    READONLY = "READONLY"
    EDITABLE = "EDITABLE"
    HIDDEN = "HIDDEN"

class McFieldInputElementType(Enum):
    TEXT= "text"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime-local"
    EMAIL = "email"

def empty_list():
    return []

@dataclass
class McFieldAction:
    event: str
    callback: typing.Callable[[str], str]

@dataclass
class McField:
    field_id: str
    label: str
    width: str
    required: bool
    visibility: McFieldVisibilityType
    input_type: McFieldInputElementType | None
    actions: typing.List[McFieldAction] = dataclasses.field(init=False)

    def __post_init__(self):
        self.actions = []

@dataclass
class McEmptySpace:
    visibility: McFieldVisibilityType = McFieldVisibilityType.READONLY
    field_id: str = ""

@dataclass
class McFieldsList:
    id: str
    caption: str
    fields: typing.List[McField] = dataclasses.field(init=False)

    def __post_init__(self):
        self.fields = []

@dataclass
class McFieldsContainer:
    id: str
    caption: str
    type: McFieldsSetType
    collapsable: bool
    fields: typing.List[McField | McEmptySpace] = dataclasses.field(init=False)

    def __post_init__(self):
        self.fields = []

@dataclass
class McTabBox:
    id: str
    caption: str
    field_sets: typing.List[McFieldsContainer] = dataclasses.field(init=False)

    def __post_init__(self):
        self.field_sets = []

class McModelObject:
    """
    Definisce come un oggetto SqlModel viene renderizzato in una pagina web
    ListView definisce gli attributi per il rendering in una <table>
    FormView definisce gli attributi per il rendering in una <form>

    Attributi della classe:
    - db_model: riferemento alla classe SQLModel
    """
    header_box: McFieldsContainer = None
    tabs: typing.List[McTabBox] = None
    fields_list: McFieldsContainer = None
    name: str = None

    def __init__(self):
        self.tabs = []

class McModelObjectBuilder:

    _mc_model_object: McModelObject = None
    _current_tab_box: McTabBox = None
    _current_fields_container: McFieldsContainer | McFieldsList = None
    _current_field: McField | None = None
    _field_ids: typing.List[str] = None

    def __init__(self):
        self._mc_model_object = McModelObject()
        self._field_ids = []

    def set_name(self, name: str):
        self._mc_model_object.name = name
        return self

    def add_tab_box(self, identity: str, caption: str):
        self._current_tab_box = McTabBox(id=identity, caption=caption)
        self._mc_model_object.tabs.append(self._current_tab_box)
        return self

    def add_fields_set(self,
                       identity: str,
                       caption: str,
                       collapsable: bool = True,
                       type: McFieldsSetType = McFieldsSetType.BLOC):
        assert self._current_tab_box is not None
        self._current_fields_container = McFieldsContainer(id=identity,
                                                           caption=caption,
                                                           type=type,
                                                           collapsable=collapsable)
        self._current_tab_box.field_sets.append(self._current_fields_container)
        return self

    def set_field_list(self, identity: str):
        self._current_fields_container = McFieldsList(id=identity, caption="")
        self._mc_model_object.fields_list = self._current_fields_container
        return self

    def set_header_box(self, identity: str):
        self._current_fields_container = McFieldsContainer(id=identity,
                                                           caption="",
                                                           type=McFieldsSetType.BLOC,
                                                           collapsable=False)
        self._mc_model_object.header_box = self._current_fields_container
        return self

    @overload
    def add_field(self,
                  field: str,
                  label: str,
                  width: str,
                  required: bool = False,
                  visibility: McFieldVisibilityType = McFieldVisibilityType.EDITABLE,
                  input_type: McFieldInputElementType = None
                  ) : ...

    @overload
    def add_field(self, field: McField,
                  label: str = ...,
                  width: str = ...,
                  required: bool = ...,
                  visibility: McFieldVisibilityType = ...,
                  input_type: McFieldInputElementType = ...
                  ) : ...

    def add_field(self,
                  field: str | McField,
                  label: str = None,
                  width: str = "100%",
                  required: bool = False,
                  visibility: McFieldVisibilityType = McFieldVisibilityType.EDITABLE,
                  input_type: McFieldInputElementType = None
                  ) :

        assert self._mc_model_object is not None
        assert self._current_fields_container is not None

        fld: McField = None
        if isinstance(field, str):
            fld = McField(field_id=field,
                                     label=label,
                                     width=width,
                                     required=required,
                                     visibility=visibility,
                                     input_type=input_type)
             #self._current_fields_container.fields.append(fld)
        elif isinstance(field, McField):
            fld = field

        self._current_field = None
        if isinstance(self._current_fields_container, McFieldsContainer):
            assert fld.field_id not in self._field_ids
            self._field_ids.append(fld.field_id)
            self._current_field = fld

        self._current_fields_container.fields.append(fld)
        return self

    def add_empty_space(self):
        assert self._mc_model_object is not None
        assert self._current_fields_container is not None
        self._current_fields_container.fields.append(McEmptySpace())
        return self

    def add_action(self, event: str, callback: typing.Callable[[str], str]):
        assert self._current_field is not None
        self._current_field.actions.append(McFieldAction(event=event, callback=callback))
        return self


    def build(self) -> McModelObject:
        assert self._mc_model_object is not None
        assert self._mc_model_object.name is not None
        return self._mc_model_object

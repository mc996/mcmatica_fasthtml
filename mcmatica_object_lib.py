from dataclasses import dataclass
import dataclasses
import typing
from typing import Generic, Literal, overload

#T = typing.TypeVar("T")

def empty_list():
    return []

@dataclass
class McField:
    field_id: str
    label: str
    width: str
#    in_list: bool
#    in_form: bool
#    list_position: int | None
#    form_position: int | None
    required: bool
    visibility: Literal["readonly", "editable", "hidden"]
    input_type: Literal["text", "number", "date", "datetime", "email"] | None



@dataclass
class McFieldsContainer:
    id: str
    caption: str
    fields: typing.List[McField] = dataclasses.field(init=False)

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

    tabs: typing.List[McTabBox] = None
    #fields_sets: typing.List[McFieldsSet] = None
    fields_list: McFieldsContainer = None
    name: str = None

    def __init__(self):
        self.tabs = []

class McModelObjectBuilder:

    _mc_model_object: McModelObject = None
    _current_tab_box: McTabBox = None
    _current_fields_container: McFieldsContainer = None

    def __init__(self):
        self._mc_model_object = McModelObject()

    def set_name(self, name: str):
        self._mc_model_object.name = name
        return self

    def add_tab_box(self, identity: str, caption: str):
        self._current_tab_box = McTabBox(id=identity, caption=caption)
        self._mc_model_object.tabs.append(self._current_tab_box)
        return self

    def add_fields_set(self, identity: str, caption: str):
        assert self._current_tab_box is not None
        self._current_fields_container = McFieldsContainer(id=identity, caption=caption)
        self._current_tab_box.field_sets.append(self._current_fields_container)
        return self

    def set_field_list(self, identity: str):
        self._current_fields_container = McFieldsContainer(id=identity, caption="")
        self._mc_model_object.fields_list = self._current_fields_container
        return self

    @overload
    def add_field(self,
                  field: str,
                  label: str,
                  width: str,
                  required: bool = False,
                  visibility: Literal["readonly", "editable", "hidden"] = "editable",
                  input_type: Literal["text", "number", "date", "datetime", "email"] = None
                  ) : ...

    @overload
    def add_field(self, field: McField,
                  label: str = ...,
                  width: str = ...,
                  required: bool = ...,
                  visibility: Literal["readonly", "editable", "hidden"] = ...,
                  input_type: Literal["text", "number", "date", "datetime", "email"] = ...
                  ) : ...

    def add_field(self,
                  field: str | McField,
                  label: str = None,
                  width: str = "100%",
                  required: bool = False,
                  visibility: Literal["readonly", "editable", "hidden"] = "editable",
                  input_type: Literal["text", "number", "date", "datetime", "email"] = None
                  ) :

        assert self._mc_model_object is not None
        assert self._current_fields_container is not None
        if isinstance(field, str):
            fld: McField = McField(field_id=field,
                                     label=label,
                                     width=width,
                                     required=required,
                                     visibility=visibility,
                                     input_type=input_type)
            self._current_fields_container.fields.append(fld)
        else:
            self._current_fields_container.fields.append(field)

        return self


    def build(self) -> McModelObject:
        assert self._mc_model_object is not None
        assert self._mc_model_object.name is not None
        return self._mc_model_object

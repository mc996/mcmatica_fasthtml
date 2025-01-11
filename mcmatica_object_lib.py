from dataclasses import dataclass
import typing
from typing import Generic, Literal, overload

#T = typing.TypeVar("T")


@dataclass
class McField:
    field_id: str
    label: str
    width: str
    in_list: bool
    in_form: bool
    list_position: int | None
    form_position: int | None
    required: bool
    visibility: Literal["readonly", "editable", "hidden"]
    input_type: Literal["text", "number", "date", "datetime", "email"] | None


class McModelObject:
    """
    Definisce come un oggetto SqlModel viene renderizzato in una pagina web
    ListView definisce gli attributi per il rendering in una <table>
    FormView definisce gli attributi per il rendering in una <form>

    Attributi della classe:
    - db_model: riferemento alla classe SQLModel
    """

    #_db_model: T = None
    _fields: typing.List[McField] = None
    _name: str = None

    def __init__(self):
        self._fields = []

    @property
    def fields(self):
        return self._fields

    @property
    def name(self):
        return self._name

class McModelObjectBuilder:

    _mc_model_object: McModelObject = None

    def __init__(self):
        self._mc_model_object = McModelObject()

    # def set_db_model(self, db_model: T ):
    #     self._mc_model_object._db_model = db_model
    #     return self

    def set_name(self, name: str):
        self._mc_model_object._name = name
        return self

    @overload
    def add_field(self,
                  field: str,
                  label: str,
                  width: str,
                  in_list: bool = True,
                  in_form: bool = False,
                  required: bool = False,
                  list_position: int | None = None,
                  form_position: int | None = None,
                  visibility: Literal["readonly", "editable", "hidden"] = "editable",
                  input_type: Literal["text", "number", "date", "datetime", "email"] = None
                  ) : ...

    @overload
    def add_field(self, field: McField,
                  label: str = ...,
                  width: str = ...,
                  in_list: bool = ...,
                  in_form: bool = ...,
                  required: bool = ...,
                  list_position: int | None = ...,
                  form_position: int | None = ...,
                  visibility: Literal["readonly", "editable", "hidden"] = ...,
                  input_type: Literal["text", "number", "date", "datetime", "email"] = ...
                  ) : ...

    def add_field(self,
                  field: str | McField,
                  label: str = None,
                  width: str = "100%",
                  in_list: bool = True,
                  in_form: bool = True,
                  required: bool = False,
                  list_position: int | None = None,
                  form_position: int | None = None,
                  visibility: Literal["readonly", "editable", "hidden"] = "editable",
                  input_type: Literal["text", "number", "date", "datetime", "email"] = None
                  ) :

        assert self._mc_model_object is not None
        if isinstance(field, str):
            field: McField = McField(field_id=field,
                                     label=label,
                                     width=width,
                                     in_list=in_list,
                                     in_form=in_form,
                                     required=required,
                                     list_position=list_position,
                                     form_position=form_position,
                                     visibility=visibility,
                                     input_type=input_type)
        #    self._mc_model_object._fields.append(field)

        if field.list_position is None:
            field.list_position = (len(self._mc_model_object._fields)+1)*10000
        if field.form_position is None:
            field.form_position = (len(self._mc_model_object._fields)+1)*10000

        self._mc_model_object._fields.append(field)
        return self


    def build(self) -> McModelObject:
        assert self._mc_model_object is not None
        assert self._mc_model_object.name is not None
        return self._mc_model_object

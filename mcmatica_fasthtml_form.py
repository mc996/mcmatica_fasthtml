from fasthtml import ft
from fasthtml import FastHTML
import typing

from pydantic import  Field
from typing_extensions import Generic, Optional

#from mcmatica_lib import McSqlModelInfo, InputTypeEnum
from mcmatica_object_lib import McModelObject, McField

T = typing.TypeVar("T")

class McFastHTMLFieldsSet:
    _data_object: McModelObject
    _identity: str = None
    _caption: str = None
    _fast_html_app: FastHTML = None
    _num_cols: int = None
    _collapsable: bool = None

    def __init__(self, app: FastHTML, data_object: McModelObject, identity: str,
                 caption: str,
                 layout_num_cols: int = 1,
                 collapsable: bool = False):
        self._fast_html_app = app
        self._data_object = data_object
        self._identity = identity
        self._caption = caption
        self._num_cols = layout_num_cols
        self._collapsable = collapsable

    def render(self):
        fields_div: typing.List[ft.Div] = []
        fields: typing.List[McField] = [f for f in self._data_object.fields if f.in_form and f.visibility != "hidden"]
        fields: typing.List[McField] = sorted(fields, key=lambda d: getattr(d, "form_position"))
        for col in fields:
            #info: McSqlModelInfo = col.json_schema_extra
            label: ft.Label = ft.Label(col.label, cls="col-4 col-form-label text-end")
            readonly: bool = False
            if col.visibility == "readonly":
                readonly = True
            input_element: ft.Div = ft.Div(ft.Input("",
                                                    type=col.input_type,
                                                    readonly=readonly,
                                                    cls="form-control", id=f"{self._identity}_pp",
                                                    **dict(placeholder=col.label)),
                                           cls="col-8"
                                           )
            fields_div.append(ft.Div(ft.Div(label, input_element, cls="row"), cls="col"))
        card: ft.Div = ft.Div(cls="card")
        card_body: ft.Div = ft.Div(cls="card-body")
        card_title: ft.Div = ft.Div( cls="card-title")

        if self._collapsable:
            card_title.set(ft.A(f"{self._caption}",
                           **{"data-bs-toggle": "collapse",
                              "data-bs-target": f"#{self._identity}",
                              "aria-expanded": "true",
                              "aria-controls": f"{self._identity}"}
                           ))

        else:
            card_title.set(f"{self._caption}")
        card_body.set(card_title, ft.Div(*fields_div, id=f"{self._identity}", cls=f"row row-cols-{self._num_cols} collapse show"))
        card.set(card_body)
        return card

    #def fill(self, data: [T]):


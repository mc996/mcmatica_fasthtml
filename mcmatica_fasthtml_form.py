from fasthtml import ft
from fasthtml import FastHTML
import typing

from pydantic import  Field
from typing_extensions import Generic, Optional

from mcmatica_lib import McSqlModelInfo, InputTypeEnum

T = typing.TypeVar("T")

class McFastHTMLFieldsSet:
    _fields: typing.List[Field]
    _identity: str = None
    _caption: str = None
    _fast_html_app: FastHTML = None
    _num_cols: int = None
    _collapsable: bool = None

    def __init__(self, app: FastHTML, fields: typing.List[Field], identity: str,
                 caption: str,
                 layout_num_cols: int = 1,
                 collapsable: bool = False):
        self._fast_html_app = app
        self._fields = fields
        self._identity = identity
        self._caption = caption
        self._num_cols = layout_num_cols
        self._collapsable = collapsable

    def render(self):
        fields_div: typing.List[ft.Div] = []
        for col in self._fields:
            info: McSqlModelInfo = col.json_schema_extra
            label: ft.Label = ft.Label(info.label, cls="col-4 col-form-label text-end")

            input_type: str = ""
            if info.input_type == InputTypeEnum.NUMBER:
                input_type = "number"
            elif info.input_type == InputTypeEnum.DATE:
                input_type = "date"

            input_element: ft.Div = ft.Div(ft.Input("",
                                                    type=input_type,
                                                    cls="form-control", id=f"{self._identity}_pp",
                                                    **dict(placeholder=info.label)),
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


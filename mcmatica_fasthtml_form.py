
from socket import send_fds

from fasthtml import ft
from fasthtml import FastHTML
import typing

from sqlmodel import SQLModel, Field

from mcmatica_object_lib import McTabBox, McField

#T = typing.TypeVar("T")

class McFastHTMLForm:
    pass

class McFastHTMLTabs:
    _tabs: typing.List[McTabBox] = None
    _fast_html_app: FastHTML = None
    _identity: str = None
    _load_data: typing.Callable[[int], typing.List[any]] = None

    def __init__(self,
                 app: FastHTML,
                 tabs: typing.List[McTabBox],
                 identity: str,
                 load_data: typing.Callable[[int], typing.List[any]]
                 ):
        self._fast_html_app = app
        self._tabs = tabs
        self._identity = identity
        self._load_data = load_data


    def _build_tab(self, tab: McTabBox, index: int, record_num: int) -> ft.Div:
        fields_set_list: typing.List[ft.Div] = []
        for fields_set in tab.field_sets:
            fields_set_list.append(McFastHTMLFieldsSet(app=self._fast_html_app,
                                fields=fields_set.fields,
                                caption=fields_set.caption,
                                load_data=self._load_data,
                                identity=fields_set.id,
                                collapsable=True,
                                layout_num_cols=2).render(record_num=record_num))
        cls: str = "tab-pane fade"
        if index == 1:
            cls += " show active"
        return ft.Div(*fields_set_list,
               cls=cls,
               id=f"content-{tab.id}",
               role="tabpanel",
               **{"aria-labelledby":f"{tab.id}",
                  "tabindex":"0"}
               )


    def render(self, record_num: int = 0) -> ft.Div:
        tab_list: typing.List[ft.Li] = []
        tab_content: typing.List[ft.Div] = []
        index: int = 0
        for  tab in self._tabs:
            index += 1
            selected: str = "false"
            cls = "nav-link"
            if index == 1:
                selected = "true"
                cls += " active"
            button = ft.Button(tab.caption,
                               role="tab",
                               cls=cls,
                               id=f"button-{tab.id}",
                               **{"data-bs-toggle":"tab",
                               "data-bs-target":f"#content-{tab.id}",
                               "aria-controls":f"{tab.id}",
                               "aria-selected":f"{selected}"})
            tab_list.append(ft.Li(button, cls="nav-item"))
            tab_content.append(self._build_tab(tab=tab, index=index, record_num=record_num))

        ul = ft.Ul(*tab_list, clS="nav nav-tabs", role="tablist")
        content = ft.Div(*tab_content, cls="tab-content")
        return ft.Div(ul, content)




class McFastHTMLFieldsSet:
    _fields: typing.List[McField] = None
    _identity: str = None
    _caption: str = None
    _fast_html_app: FastHTML = None
    _num_cols: int = None
    _collapsable: bool = None
    _load_data: typing.Callable[[int], typing.List[any]] = None

    def __init__(self, app: FastHTML,
                 fields: typing.List[McField], identity: str,
                 caption: str,
                 load_data: typing.Callable[[int], typing.List[any]],
                 layout_num_cols: int = 1,
                 collapsable: bool = False):
        self._fast_html_app = app
        self._fields: typing.List[McField] = fields
        self._identity = identity
        self._caption = caption
        self._load_data = load_data
        self._num_cols = layout_num_cols
        self._collapsable = collapsable

    def render(self, record_num: int = 0) -> ft.Div:
        fields_div: typing.List[ft.Div] = []
        fields: typing.List[McField] = [f for f in self._fields if f.visibility != "hidden"]

        data = None
        if record_num > 0:
            data = self._load_data(record_num)

        for col in fields:
            value = ""
            if data is not None:
                value = getattr(data, col.field_id)
            label: ft.Label = ft.Label(col.label, cls="col-4 col-form-label text-end")
            readonly: bool = False
            if col.visibility == "readonly":
                readonly = True

            input_element: ft.Div = ft.Div(ft.Input("",
                                                    type=col.input_type,
                                                    readonly=readonly,
                                                    cls="form-control",
                                                    id=f"{self._identity}",
                                                    value=value,
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



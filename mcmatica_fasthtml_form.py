from babel.plural import cldr_modulo
from fasthtml import ft
from fasthtml import FastHTML
import typing

from mcmatica_fasthtml_table import McFastHTMLTable
from mcmatica_object_lib import McTabBox, McField, McFieldsSetType, McModelObject, McEmptySpace


#T = typing.TypeVar("T")

class McFastHTMLWindow:
    _object_model: McModelObject
    _fast_html_app: FastHTML = None
    _load_data: typing.Callable[[int, int, typing.Optional[str], bool], typing.List[any]] = None
    _list: McFastHTMLTable = None


    def __init__(self,
                 app: FastHTML,
                 object_model: McModelObject,
                 load_data: typing.Callable[[int, int, typing.Optional[str], bool], typing.List[any]] = None
        ):
        self._fast_html_app = app
        self._object_model = object_model
        self._load_data = load_data

    def _get_record(self, record_num: int) -> any:
        if self._list is not None:
            return self._list.dataset[record_num]
        else:
            return None

    def _build_main_layout(self):
        panel: ft.Div = ft.Div(cls="row ", style={"height":"90vh"})
        left_panel: ft.Div = ft.Div(self._build_list(),
                                    cls="col-3 p-3 bg-body-tertiary overflow-x-auto ")

        separator: ft.Div = ft.Div("", cls="flex-shrink-0 height-100vh")

        tab_div: ft.Div = ft.Div(self._build_tabs(), cls="mt-5 vh-100")

        right_panel: ft.Div = ft.Div(ft.Div(
                                     self._build_main_box(),
                                     tab_div,
                                     cls="bg-body-tertiary"),
                                     cls="col-9 overflow-y-auto", style={"height":"90vh"})
        panel.set(left_panel, right_panel)
        return panel

    def _build_list(self):
        self_list: McFastHTMLTable = McFastHTMLTable(app=self._fast_html_app,
                                                 fields=self._object_model.fields_list.fields,
                                                 identity='hero',
                                                 load_data= self._load_data,
                                                 num_rows=6)
        return self_list.render()

    def _build_main_box(self):
        return McFastHTMLFieldsSet(app=self._fast_html_app,
                            fields=self._object_model.header_box.fields,
                            caption=self._object_model.header_box.caption,
                            load_data=self._get_record,
                            identity=self._object_model.header_box.id,
                            collapsable=False,
                            layout_num_cols=2).render(record_num=1)


    def _build_tabs(self):
        return McFastHTMLTabs(app=self._fast_html_app,
                                             identity="tabs",
                                             tabs=self._object_model.tabs,
                                             load_data=self._get_record).render()

    def render(self):
        container: ft.Div = ft.Div(cls="container-fluid vh-100 ")
        #ft.Label(self._object_model.name)
        nav_div: ft.Nav = McFastHTMLFormNavBar(app=self._fast_html_app).render()
        header_panel: ft.Div = ft.Div(nav_div,
                                 cls="row ", style={"height":"5vh"}
                                 )
        foot_panel: ft.Div = ft.Div("foot", cls="row", style={"height":"5vh"})

        hidden_data_div: ft.Div = ft.Div("", id="hidden_data", hidden=True)

        container.set(hidden_data_div,
                      header_panel,
                      self._build_main_layout(),
                      foot_panel)

        return container


class McFastHTMLFormNavBar:
    _fast_html_app: FastHTML = None

    def __init__(self,
                 app: FastHTML):
        self._fast_html_app = app

    def render(self) -> ft.Nav:
        button_delete: ft.Li = ft.Li(ft.A("delete", cls="nav-link"), cls="nav-item")
        button_save: ft.Li = ft.Li(ft.A("save", cls="nav-link"), cls="nav-item")

        ul: ft.Ul = ft.Ul(button_delete,
                          button_save,
                          cls="navbar-nav")
        div_navbar: ft.Div = ft.Div(ul,cls="collapse navbar-collapse")
        nav: ft.Nav = ft.Nav(div_navbar,cls="navbar navbar-expand-lg bg-body-tertiary")
        return nav


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
            if fields_set.type == McFieldsSetType.BLOC:
                fields_set_list.append(McFastHTMLFieldsSet(app=self._fast_html_app,
                                    fields=fields_set.fields,
                                    caption=fields_set.caption,
                                    load_data=self._load_data,
                                    identity=fields_set.id,
                                    collapsable=fields_set.collapsable,
                                    layout_num_cols=2).render(record_num=record_num))
            elif fields_set.type == McFieldsSetType.GRID:
                card: ft.Div = ft.Div(cls="card")
                card_body: ft.Div = ft.Div(cls="card-body")
                card_title: ft.Div = ft.Div(cls="card-title")
                if fields_set.collapsable:
                    card_title.set(ft.A(f"{fields_set.caption}",
                                        **{"data-bs-toggle": "collapse",
                                           "data-bs-target": f"#{fields_set.id}",
                                           "aria-expanded": "true",
                                           "aria-controls": f"{fields_set.id}"}
                                        ))

                else:
                    card_title.set(f"{fields_set.caption}")
                card_body.set(card_title, ft.Div(McFastHTMLTable(app=self._fast_html_app,
                                                      identity=fields_set.id,
                                                      load_data=None,
                                                       data=[],
                                                      fields=fields_set.fields,
                                                      num_rows=10
                                                     ).render(),
                                                 id=f"{fields_set.id}",
                                                 ))
                card.set(card_body)

                fields_set_list.append(card)


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
        return ft.Div(ul, content, id=f"form_{self._identity}")




class McFastHTMLFieldsSet:
    _fields: typing.List[McField | McEmptySpace] = None
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
        fields: typing.List[McField | McEmptySpace] = [f for f in self._fields if f.visibility != "hidden"]

        data = None
        if record_num > 0:
            data = self._load_data(record_num)

        for col in fields:
            if isinstance(col, McField):
                value = ""
                if data is not None:
                    value = getattr(data, col.field_id)
                label: ft.Label = ft.Label(col.label, cls="col-4 col-form-label text-end")
                readonly: bool = False
                if col.visibility == "readonly":
                    readonly = True

                #id = f"{self._identity}-{col.field_id}",
                input_element: ft.Div = ft.Div(ft.Input("",
                                                        type="text" if col.input_type is None else col.input_type.value,
                                                        readonly=readonly,
                                                        cls="form-control",
                                                        id=f"{col.field_id}",
                                                        value=value,
                                                        **dict(placeholder=col.label)),
                                               cls="col-8"
                                               )
                fields_div.append(ft.Div(ft.Div(label, input_element, cls="row"), cls="col"))
            elif isinstance(col, McEmptySpace):
                fields_div.append(ft.Div(ft.Div("", cls="row"), cls="col"))
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



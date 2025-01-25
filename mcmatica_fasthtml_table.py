from fasthtml import ft
from fasthtml import FastHTML
import typing

from starlette.routing import Route
from typing_extensions import  Optional

from mcmatica_object_lib import McField
import orjson

#T = typing.TypeVar("T")

class McFastHTMLTable:
    _fields: typing.List[McField] = None
    _identity: str = None
    _load_data: typing.Callable[[int, int, Optional[str], bool], typing.List[any]] = None
    _data: typing.List[any] = None
    _offset: int = 0
    _limit: int = 5
    _fast_html_app: FastHTML = None
    _sort_field: typing.Optional[str] = None
    _sort_reverse: bool = False
    _record_count: int = 0
    _loaded_dataset: typing.List[any] = None

    def  __init__(self,
                  app: FastHTML,
                  fields: typing.List[McField],
                  identity: str,
                  load_data: typing.Callable[[int, int, Optional[str], bool], typing.List[any]] | None,
                  data: typing.List[any] = None,
                  num_rows: int = 0):
        self._fields = fields
        self._identity = identity
        self._load_data = load_data
        self._data = data
        self._fast_html_app = app
        self._limit = num_rows
        self._record_count: int = 0

        # Sort path
        route_sort = Route(path=f"/{self._identity}/sort",
                  endpoint=self._fast_html_app._endp(self.sort, None),
                  methods=['GET'],
                  name=f"{self._identity}_sort",
                  include_in_schema=True)
        self._fast_html_app.add_route(route_sort)

        # pagination path
        route_page = Route(path=f"/{self._identity}/page",
                  endpoint=self._fast_html_app._endp(self.page, None),
                  methods=['GET'],
                  name=f"{self._identity}_page",
                  include_in_schema=True)
        self._fast_html_app.add_route(route_page)

        route_record = Route(path=f"/{self._identity}/record",
                  endpoint=self._fast_html_app._endp(self.load_record, None),
                  methods=['GET'],
                  name=f"{self._identity}_record",
                  include_in_schema=True)
        self._fast_html_app.add_route(route_record)


    def _build_thead(self) -> (ft.Style, ft.Thead):
        cls: str = "link-light link-underline-opacity-0 link-underline-opacity-100-hover link-offset-2 d-block"

        cols: typing.List[ft.Th] = []
        cols_style: str = ""
        for col in self._fields:
            label: str = col.label
            if col.field_id == self._sort_field:
                if self._sort_reverse:
                    label += " ↑"
                else:
                    label += " ↓"
            cols.append(ft.Th(ft.Div(ft.A(label,
                                                hx_get=f"/{self._identity}/sort?field={col.field_id}",
                                                hx_target=f"#{self._identity}-table",
                                                cls=cls
                                          ),
                                        ),
                              cls=f"col_{col.field_id}", scope="col", **{'data-theme':"dark"})
                        )
            cols_style += f"""
                            .{self._identity} .col_{col.field_id} {{
                                width: {col.width}
                            }}
                            """
        th_cols = ft.Tr(*cols)
        return ft.Style(cols_style), ft.Thead( th_cols, id=f"{self._identity}-thead", cls="table-dark")

    def _build_tbody(self) -> ft.Tbody:
        rows: typing.List[ft.Tr] = []
        if self._load_data is not None:
            self._record_count, self._loaded_dataset = self._load_data(self._offset, self._limit, self._sort_field, self._sort_reverse)
        else:
            self._loaded_dataset = self._data
            self._record_count = len(self._loaded_dataset)
        count: int = 0
        for model in self._loaded_dataset:
            fields: typing.List[ft.Td] = []
            for col in self._fields:
                fields.append(ft.Td(ft.Div(getattr(model, col.field_id), cls=f"col_{col.field_id}"), scope="row"))
            rows.append(ft.Tr(*fields,
                              role="button",
                              hx_get=f"/{self._identity}/record?record_num={count}",
                              hx_target="#hidden_data",
                              **{"hx-on:htmx:after-request": "fill_inputs_form('form_tabs1','hidden_data');"}
                              ))
            count += 1

        return ft.Tbody(*rows, id=f"{self._identity}-tbody")

    def _build_tfoot(self) -> ft.Tfoot:
        commands: typing.List[ft.Li] = [
            ft.Li(ft.A("<<",
                       hx_get=f"/{self._identity}/page?direction=first",
                       hx_target=f"#{self._identity}-table",
                       cls="page-link"),
                  cls="page-item"),
            ft.Li(ft.A("<",
                       hx_get=f"/{self._identity}/page?direction=prev",
                       hx_target=f"#{self._identity}-table",
                       cls="page-link"),
                  cls="page-item"),
            ft.Li(f"{int(self._offset / self._limit) + 1} of {int(self._record_count / self._limit) + 1}", cls="ps-5 pe-5"),
            ft.Li(ft.A(">",
                       hx_get=f"/{self._identity}/page?direction=next",
                       hx_target=f"#{self._identity}-table",
                       cls="page-link"),
                  cls="page-item"),
            ft.Li(ft.A(">>",
                       hx_get=f"/{self._identity}/page?direction=last",
                       hx_target=f"#{self._identity}-table",
                       cls="page-link"),
                  cls="page-item")
        ]
        pagination: ft.Ul = ft.Ul(*commands,cls="pagination pagination-sm")
        nav: ft.Nav = ft.Nav(
            pagination
        )
        foot: ft.Tfoot = ft.Tfoot(ft.Tr(ft.Td(nav,colspan=len(self._fields))))
        return foot

    async def sort(self, field: str):
        if self._sort_field == field:
             self._sort_reverse = not self._sort_reverse
        else:
             self._sort_reverse = False
        self._sort_field = field
        return self.render()

    async def page(self, direction: str):
        if direction == "next":
            if self._offset + self._limit < self._record_count:
                self._offset += self._limit
        elif direction == "prev":
            self._offset -= self._limit
            if self._offset < 0:
                self._offset = 0
        elif direction == "first":
            self._offset = 0
        elif direction == "last":
            self._offset = int(self._record_count / self._limit) * self._limit
        return self.render()

    async def load_record(self, record_num: int):
        print(self._loaded_dataset[record_num].model_dump())
        return orjson.dumps(self._loaded_dataset[record_num].model_dump()).decode()


    @property().getter
    def dataset(self):
        return self._loaded_dataset
        
        
    def render(self):
        col_style, th = self._build_thead()
        tb = self._build_tbody()
        tf = self._build_tfoot()
        table: ft.Div = ft.Div(col_style,
                               ft.Div(
                                   ft.Table(th, tb, tf,
                                    cls="table table-striped table-hover fixed_header responsive"),
                                    id=f"{self._identity}-table",
                                    hx_indicator=".loader",
                                    cls=self._identity
                               )
                               )
        return table
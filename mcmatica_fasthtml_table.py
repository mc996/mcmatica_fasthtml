from fasthtml import ft
from fasthtml import FastHTML
import typing

from starlette.responses import PlainTextResponse, HTMLResponse
from starlette.routing import Route
from starlette.types import Scope, Receive, Send
from typing_extensions import Generic, Optional
from pydantic import  Field
from websockets.http11 import Request

#from starlette.routing import Route

T = typing.TypeVar("T")




class McFastHTMLTable(Generic[T]):
    _db_model: T = None
    _identity: str = None
    _load_data: typing.Callable[[int, int, Optional[str], bool], typing.List[any]] = None
    _offset: int = 0
    _limit: int = 15
    _fast_html_app: FastHTML = None
    _sort_field: typing.Optional[str] = None
    _sort_reverse: bool = False
    _cls: typing.Optional[str] = None

    def  __init__(self, app: FastHTML, db_model: T, identity: str,
                  load_data: typing.Callable[[int, int, Optional[str], bool], typing.List[any]],
                  cls: Optional[str]):
        self._db_model = db_model
        self._identity = identity
        self._load_data = load_data
        self._fast_html_app = app
        self._cls = cls

        r = Route(path=f"/{self._identity}/sort",
                  endpoint=self._fast_html_app._endp(self.sort, None),
                  methods=['GET'],
                  name=f"{self._identity}_sort",
                  include_in_schema=True)
        self._fast_html_app.add_route(r)

        print(self._fast_html_app.routes)

    def _build_thead(self) -> (ft.Style, ft.Thead):
        cls: str = "link-light link-underline-opacity-0 link-underline-opacity-100-hover link-offset-2 d-block"

        cols: typing.List[ft.Th] = []
        cols_style: str = ""
        for key in self._db_model.model_fields.keys():
            col: Field = self._db_model.model_fields[key]
            cols.append(ft.Th(ft.Div(ft.A(f"{col.title}",
                                                hx_get=f"/{self._identity}/sort?field={key}",
                                                hx_target=f"#{self._identity}-table",
                                                cls=cls
                                          ),
                                        ),
                              cls=f"col_{key}", scope="col", **{'data-theme':"dark"})
                        )
            cols_style += f"""
                .{self._identity} .col_{key} {{
                    width: {col.json_schema_extra['width']}
                }}
                """
        th_cols = ft.Tr(*cols)
        return ft.Style(cols_style), ft.Thead( th_cols, id=f"{self._identity}-thead", cls="table-dark")

    def _build_tbody(self) -> ft.Tbody:
        rows: typing.List[ft.Tr] = []
        for model in self._load_data(self._offset, self._limit, self._sort_field, self._sort_reverse):
            fields: typing.List[ft.Td] = []
            for key in self._db_model.model_fields.keys():
                fields.append(ft.Td(ft.Div(getattr(model, key), cls=f"col_{key}"), scope="row"))
            rows.append(ft.Tr(*fields))

        return ft.Tbody(*rows, id=f"{self._identity}-tbody")

    async def sort(self, field: str):
        if self._sort_field == field:
             self._sort_reverse = not self._sort_reverse
        else:
             self._sort_reverse = False
        self._sort_field = field
        return self.render()



    def render(self):
        col_style, th = self._build_thead()


        tb = self._build_tbody()
        table: ft.Div = ft.Div(col_style,
                               ft.Div(
                                   ft.Table(th, tb, cls=self._cls),
                                   id=f"{self._identity}-table",
                                   hx_indicator=".loader",
                                   cls=self._identity
                               )
                               )
        return table
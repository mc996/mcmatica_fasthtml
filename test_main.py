import time
import typing
from typing import Optional
from fasthtml import FastHTML, fastapp
from fasthtml import ft
from fasthtml.fastapp import fast_app
from sqlmodel import Field, SQLModel
from operator import itemgetter

from mcmatica_lib import SqlModelInfo, InputTypeEnum
from mcmatica_fasthtml_table import McFastHTMLTable

class Hero(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True,
                              title="Id", schema_extra=dict(json_schema_extra={"width":"150px"}))
    name: str = Field(title="Nome",schema_extra=dict(json_schema_extra={"width":"300px"}))
    secret_name: str = Field(title="Segreto",schema_extra=dict(json_schema_extra={"width":"300px"}))
    age: Optional[int] = Field(default=None, title="Età", schema_extra=dict(json_schema_extra={"width":"300px"}))

pico = (ft.Link(rel='stylesheet',
                     href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css',
                     type='text/css'))
app = FastHTML(debug=True, hdrs=pico)

tailwind = (ft.Script(src="https://cdn.tailwindcss.com"))
#app = FastHTML(debug=True, hdrs=tailwind)

bootstrap = (ft.Link(rel='stylesheet',
                     href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                     type='text/css'),
             ft.Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"))
#app = FastHTML(debug=True, hdrs=bootstrap)

rt = app.route

def mock_get_data(offset: int, limit: int, sort: Optional[str], sort_reverse: bool) -> typing.List[Hero]:
    dati = [
        Hero(id=1, name="xciccio", secret_name="pppp", age=112),
        Hero(id=2, name="ciccio22", secret_name="pppp2", age=22),
        Hero(id=3, name="ciccio2", secret_name="pppp2", age=22),
    ]
    time.sleep(0)
    if sort is None:
        return dati
    else:
        return sorted(dati, key=lambda d: getattr(d, sort), reverse=sort_reverse)



@rt("/", methods=['GET'])
async def main():

    # db = SessionLocal()
    # contacts = db.query(ContactDbModel).filter(ContactDbModel.id < 1000).all()
    # db.close()
    table: McFastHTMLTable = McFastHTMLTable[Hero](app=app, db_model=Hero, identity='hero',
                                                   load_data=mock_get_data,
                                                   cls="table table-striped table-hover fixed_header responsive")
    #table: McFastHTMLTable = McFastHTMLTable(app=app, db_model=Hero, identity='hero', load_data=mock_get_data)
    #return table.render()
    #return ft.Html(ft.Head(ft.Title("TEST")),
    #                ft.Body(ft.Div(ft.Button("ciao"),
    #                               table.render()
    #                               )))
    return ft.Div(ft.Button("ciao", cls="btn btn-primary m-2"),
                  ft.Div(table.render(),
                         cls="container")
                  )


def start():
    fastapp.serve()

if __name__ == "__main__":
    start()
import time
import typing
from datetime import date, datetime
from typing import Optional
from fasthtml import FastHTML, fastapp
from fasthtml import ft
from fasthtml.fastapp import fast_app
from sqlmodel import Field, SQLModel
from operator import itemgetter

#from mcmatica_lib import McSqlModelInfo, InputTypeEnum
from mcmatica_object_lib import McModelObject, McModelObjectBuilder
from mcmatica_fasthtml_table import McFastHTMLTable
from mcmatica_fasthtml_form import McFastHTMLFieldsSet, McFastHTMLTabs

class Hero(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True,
                               title="Id")
    name: str = Field(title="Nome")
    secret_name: str = Field(title="Segreto")
    age: Optional[int] = Field(default=None, title="Età")
    country: str = Field(title="country")
    birthday: date = Field(title="BirthDay")

pico = (ft.Link(rel='stylesheet',
                     href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css',
                     type='text/css'))
#app = FastHTML(debug=True, hdrs=pico)

tailwind = (ft.Script(src="https://cdn.tailwindcss.com"))
#app = FastHTML(debug=True, pico=False, hdrs=tailwind)

bootstrap = (ft.Link(rel='stylesheet',
                     href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                     type='text/css'),
             ft.Link(rel="stylesheet",
                     href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"),
             ft.Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"))
app = FastHTML(debug=True, pico=False, hdrs=bootstrap)

rt = app.route

def mock_get_data(offset: int, limit: int, sort: Optional[str], sort_reverse: bool) -> typing.List[Hero]:
    dati = [
        Hero(id=1, name="xciccio", secret_name="pppp", age=112, country="IT", birthday=datetime.now().date()),
        Hero(id=2, name="ciccio22", secret_name="pppp2", age=22, country="NZ", birthday=datetime.now().date()),
        Hero(id=3, name="pluto 333", secret_name="pppp2", age=22, country="GB", birthday=datetime.now().date()),
    ]
    for i in range(4,30):
        dati.append(Hero(id=i, name=f"ciccio{i}", secret_name="pppp", age=11+i, country="IT", birthday=datetime.now().date()))

    time.sleep(0)

    result = dati
    if sort is not None:
        result = sorted(dati, key=lambda d: getattr(d, sort), reverse=sort_reverse)

    return result[offset:offset+limit]


@rt("/", methods=['GET'])
async def main():
    hero: McModelObject = McModelObjectBuilder() \
    .set_name("Hero") \
    .set_field_list(identity="hero_list") \
        .add_field(field="id", label="Id", width="50px") \
        .add_field(field="name", label="Nome") \
        .add_field(field="age", label="Età") \
        .add_field(field="country", label="Nazione", width="150px") \
    .add_tab_box(identity="tab_1", caption="TAB 1") \
        .add_fields_set(identity="tab1_box1", caption="Blocco 1") \
            .add_field(field="name", label="Id", required=True, input_type="text") \
            .add_field(field="age", label="Age", required=False, input_type="number") \
        .add_fields_set(identity="tab1_box2", caption="Blocco 2") \
            .add_field(field="country", label="Nazione", required=True, input_type="text") \
    .add_tab_box(identity="tab_2", caption="TAB 2") \
        .add_fields_set(identity="tab2_box1", caption="Blocco 1") \
            .add_field(field="secretname", label="Password", width="10%") \
    .build()

    table: McFastHTMLTable = McFastHTMLTable(app=app,
                                             fields=hero.fields_list.fields,
                                             identity='hero',
                                             load_data=mock_get_data,
                                             num_rows=6)



    tab: McFastHTMLTabs = McFastHTMLTabs(app=app,
                                         identity="tabs1",
                                         tabs=hero.tabs)

    return ft.Div(
                  ft.Div(table.render(),
                         tab.render(),
                         cls="container")
                  )

    #@rt("/", methods=['GET'])
# async def main():
#     object: McModelObject = McModelObjectBuilder() \
#         .set_name("hero") \
#         .add_field(field="id", label="Id", width="90px", required=True, in_form=False) \
#         .add_field(field="name", label="Nome", required=False) \
#         .add_field(field="country", label="Nazione", width="30px", required=False, form_position=1) \
#         .add_field(field="age", label="età", width="120px", required=False, visibility="readonly") \
#         .build()
#
#
#     table: McFastHTMLTable = McFastHTMLTable(app=app, data_object=object, identity='hero',
#                                                    load_data=mock_get_data,
#                                                    num_rows=6)
#
#     fields: typing.List[Field] = []
#     for key in Hero.model_fields.keys():
#         if key in ("name", "age", "country", "birthday"):
#             fields.append(Hero.model_fields[key])
#
#     blocco1: McFastHTMLFieldsSet = McFastHTMLFieldsSet(app=app, data_object=object , identity="hero-blocco1",
#                                                     layout_num_cols=1,
#                                                     caption="Blocco1",
#                                                     collapsable=True)
#     blocco2: McFastHTMLFieldsSet = McFastHTMLFieldsSet(app=app, data_object=object , identity="hero-blocco2",
#                                                     layout_num_cols=2,
#                                                     caption="Blocco numero 2 caption molto lunga",
#                                                     collapsable=True)
#
#     return ft.Div(ft.Button("ciao", cls="btn btn-primary m-2"),
#                   ft.Div(table.render(),blocco1.render(), blocco2.render(),
#                          cls="container")
#                   )


def start():
    fastapp.serve()

if __name__ == "__main__":
    start()
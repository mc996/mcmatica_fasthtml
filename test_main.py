import time
import typing
from datetime import date, datetime
from pickle import GLOBAL
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
import orjson

import i18n


i18n.set("locale", 'it')
i18n.load_path.append("locale")

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
             ft.Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"),
             ft.Script(src="mcmatica_client_lib.js")
             )
app = FastHTML(debug=True, pico=False, hdrs=bootstrap)
app.static_route(ext='.js', prefix="/", static_path='./static/js')

rt = app.route

dati = [
    Hero(id=1, name="xciccio", secret_name="pppp", age=112, country="IT", birthday=datetime.now().date()),
    Hero(id=2, name="ciccio22", secret_name="pppp2", age=22, country="NZ", birthday=datetime.now().date()),
    Hero(id=3, name="pluto 333", secret_name="pppp2", age=22, country="GB", birthday=datetime.now().date()),
]
for i in range(4, 30):
    dati.append(
        Hero(id=i, name=f"ciccio{i}", secret_name="pppp", age=11 + i, country="IT", birthday=datetime.now().date()))


def mock_get_data(offset: int, limit: int, sort: Optional[str], sort_reverse: bool) -> typing.List[Hero]:

    time.sleep(0)

    result = dati
    if sort is not None:
        result = sorted(dati, key=lambda d: getattr(d, sort), reverse=sort_reverse)

    return result[offset:offset+limit]

def mock_get_record(record_num: int) -> Hero:
    return dati[record_num]


hero: McModelObject = McModelObjectBuilder() \
.set_name("Hero") \
.set_field_list(identity="hero_list") \
    .add_field(field="id", label=i18n.t("general.id"), width="50px") \
    .add_field(field="name", label=i18n.t("general.name")) \
    .add_field(field="age", label=i18n.t("general.age")) \
    .add_field(field="secret_name", label=i18n.t("general.password"), width="250px") \
    .add_field(field="country", label=i18n.t("general.country"), width="150px") \
.add_tab_box(identity="tab_1", caption="TAB 1") \
    .add_fields_set(identity="tab1_box1", caption="Blocco 1") \
        .add_field(field="id", label="Id", required=True, input_type="text") \
        .add_field(field="name", label=i18n.t("general.name"), required=True, input_type="text") \
        .add_field(field="age", label="Age", required=False, input_type="number") \
    .add_fields_set(identity="tab1_box2", caption="Blocco 2") \
        .add_field(field="country", label="Nazione", required=True, input_type="text") \
.add_tab_box(identity="tab_2", caption="TAB 2") \
    .add_fields_set(identity="tab2_box1", caption="Blocco 1") \
        .add_field(field="secret_name", label="Password", width="10%") \
        .add_field(field="birthday", label="Data di nascita", required=False, input_type="date") \
.build()

table: McFastHTMLTable = McFastHTMLTable(app=app,
                                         fields=hero.fields_list.fields,
                                         identity='hero',
                                         load_data=mock_get_data,
                                         num_rows=6)



tab: McFastHTMLTabs = McFastHTMLTabs(app=app,
                                     identity="tabs1",
                                     tabs=hero.tabs,
                                     load_data=mock_get_record)

#rec_count = -1
@rt(path="/fill", methods=['GET'])
async def fill_data_test(sess):
    #print("sess",sess['record_count'])
    rec_count: int = 0
    if 'record_count' in sess:
        rec_count = int(sess['record_count'])
    print("rec_count",rec_count)
    sess['record_count'] = rec_count + 1
    if rec_count < len(dati):
        print(dati[rec_count].model_dump())
        return orjson.dumps(dati[rec_count].model_dump()).decode()
    else:
        return "{}"
    #return  tab.render(record_num=rec_count)

@rt(path="/fill2", methods=['GET'])
async def fill_data_test():
    global rec_count
    rec_count += 1
    return  tab.render(record_num=rec_count)


@rt("/", methods=['GET'])
async def main():

    return ft.Div(
                  ft.Div(ft.Div("", id="hidden_data", hidden=True),
                      ft.Button("button 1",
                                   cls="btn btn-primary m-2",
                                   hx_get="/fill",
                                   hx_target="#hidden_data",
                                   **{"hx-on:htmx:after-request":"fill_inputs_form('form_tabs1','hidden_data');"}),
                      ft.Button("Clear Session",
                                   cls="btn btn-primary m-2",
                                   **{"hx-on:click": "alert('ciao');"}),
                      ft.Button("button 2",
                                   cls="btn btn-primary m-2",
                                   hx_get="/fill2",
                                   hx_target="#form_tabs1",
                                   **{"hx-on:htmx:after-request":"fill_inputs_form('ciao',{'ciao':'mondo'}); alert(`event.detail.target ${event.detail.target}`);"}),
                         table.render(),
                         tab.render(record_num=0),
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
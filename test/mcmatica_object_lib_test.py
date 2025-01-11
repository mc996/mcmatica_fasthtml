import unittest
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field

from mcmatica_object_lib import McModelObjectBuilder, McModelObject


class Hero(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True,
                              title="Id")
    name: str = Field(title="Nome")
    secret_name: str = Field(title="Segreto")
    age: Optional[int] = Field(default=None, title="Età")
    country: str = Field(title="country")
    birthday: date = Field(title="BirthDay")


class MyTestCase(unittest.TestCase):

    def test_001_builder(self):
        object: McModelObject = McModelObjectBuilder() \
                                       .set_name("prova") \
                                       .add_field(field="name", label="Nome", required=True) \
                                       .add_field(field="country", label="Nazione", required=False) \
                                       .build()

        self.assertIsNotNone(object)
        print(object)
        self.assertEqual(object.name, "prova")

if __name__ == '__main__':
    unittest.main()

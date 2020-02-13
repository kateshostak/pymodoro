from json_orm import JsonORM
from sqlite_orm import SqliteORM
from xml_orm import XmlORM


class ORM(object):
    SQLITE = 'sqlite'
    JSON = 'json'
    XML = 'xml'

    DB_TYPES = {
        SQLITE: SqliteORM,
        JSON: JsonORM,
        XML: XmlORM,
    }

    @staticmethod
    def get_orm(type_, *args, **kwargs):
        return ORM.DB_TYPES[type_](*args, **kwargs)

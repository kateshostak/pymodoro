from json_orm import JsonORM
from sqlite_orm import SqliteORM


class ORM(object):
    SQLITE = 'sqlite'
    JSON = 'json'

    DB_TYPES = {
        SQLITE: SqliteORM,
        JSON: JsonORM,
    }

    @staticmethod
    def get_orm(type_, *args, **kwargs):
        return ORM.DB_TYPES[type_](*args, **kwargs)

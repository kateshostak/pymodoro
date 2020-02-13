from user import User


class XmlORM(object):
    def __init__(self, path_to_db):
        self.type = 'xml'
        self.path_to_db = path_to_db

    def create_db(self):
        try:
            with open(self.path_to_db, 'r'):
                pass
        except FileNotFoundError:
            with open(self.path_to_db, 'w'):
                pass




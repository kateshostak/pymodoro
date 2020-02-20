import xml.etree.ElementTree as ET
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

    def create_user(self, user):
        users = self.load_xml()
        for usr in users:
            if user.name in usr.attrib['name']:
                return False
        else:
            pass

    def load_xml(self):
        root = ET.parse(self.path_to_db).getroot()
        return [usr for usr in root]

    def get_user(self, name):
        users = self.load_xml()


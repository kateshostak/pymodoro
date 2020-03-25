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
        if user.name in users:
            return False

        else:
            top = ET.Element('data')
            usr = top.SubElement(top, 'user')
            usr.set('name', user.name)
            setting = top.SubElement(usr, 'setting')
            setting.set('setting', user.setting)


    def load_xml(self):
        users = ET.parse(self.path_to_db).getroot()
        return {user.find('name').text:user for user in users}

    def user_constructor(self, user_elem):
        name = user_elem.find('name').text
        settings = {setting.find('name'):setting for setting in user.elem.findall('settings')}


    def get_user(self, name, setting):
        users = self.load_xml()
        if name not in users:
            return False
        else:
            return user_constructor(users[name])


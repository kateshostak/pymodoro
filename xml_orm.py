import xml.etree.ElementTree as ET
from user import User


class XmlORM(object):
    def __init__(self, path_to_db):
        self.type = 'xml'
        self.path_to_db = path_to_db
        self.create_db()

    def create_db(self):
        try:
            with open(self.path_to_db, 'r'):
                pass
        except FileNotFoundError: # noqa
            with open(self.path_to_db, 'w') as f:
                self.create_xml(f)

    def create_xml(self, file_):
        ET.ElementTree(ET.Element('users')).write(self.path_to_db)

    def udate_user(self, user):
        pass

    def create_user(self, user):
        users = self.load_xml()
        if user.name in users:
            return False
        else:
            tree = ET.parse(self.path_to_db)
            root = tree.getroot()

            usr = ET.Element('user')
            name = ET.SubElement(usr, 'name')
            name.text = user.name

            setting = ET.SubElement(usr, 'setting')
            set_name = ET.SubElement(setting, 'name')
            set_name.text = user.setting

            work = ET.SubElement(setting, 'work')
            work.text = str(user.work)

            shortbreak = ET.SubElement(setting, 'shortbreak')
            shortbreak.text = str(user.shortbreak)

            longbreak = ET.SubElement(setting, 'longbreak')
            longbreak.text = str(user.longbreak)

            cycle = ET.SubElement(setting, 'cycle')
            cycle.text = str(user.cycle)

            root.append(usr)
            tree.write(self.path_to_db)
            return True

    def load_xml(self):
        users = ET.parse(self.path_to_db).getroot()
        return {user.find('name').text: user for user in users}

    def user_constructor(self, user_elem, setting):
        settings = {setting.find('name').text: setting for setting in user_elem.findall('setting')} # noqa
        if setting not in settings:
            return False, [name for name in settings]
        else:
            name = user_elem.find('name').text
            profile = settings[setting]
            work = int(profile.find('work').text)
            shortbreak = int(profile.find('shortbreak').text)
            longbreak = int(profile.find('longbreak').text)
            cycle = int(profile.find('cycle').text)
        return User(None, name, work, shortbreak, longbreak, cycle)

    def get_user(self, name, setting):
        users = self.load_xml()
        if name not in users:
            return False
        else:
            return self.user_constructor(users[name], setting)

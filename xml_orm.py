import xml.etree.ElementTree as ET
from user import User
from setting import Setting

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

    def delete_user(self, user):
        pass

    def udate_user(self, user):
        users = self.load_xml()
        if user.name in users:
            user_elem = users[user.name]
            profile = self.get_xml_setting(user_elem, user.setting)
            if profile:
                self.update_setting(user, user_elem, profile)
            return True
        return False

    def upadate_setting(self, user, user_elem, profile):
        profile.find('work').text = str(user.work) or profile.find('work')
        profile.find('shortbreak').text = str(user.shortbreak) or profile.find('shortbreak')
        profile.find('lonbreak').text = str(user.longbreak) or profile.find('longbreak')
        profile.find('cycle').text = str(user.cycle) or profile.find('cycle')

    def create_user(self, user):
        users = self.load_xml()
        if user.name in users:
            return False
        else:
            self.build_tree(user)
        return True

    def build_tree(self, user):
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

    def load_xml(self):
        users = ET.parse(self.path_to_db).getroot()
        return {user.find('name').text: user for user in users}

    def user_constructor(self, user_elem, set_name):
        setting = self.user_settings(user_elem, set_name)
        if setting:
            name = user_elem.find('name').text
            return User(None, name, setting)

    def user_settings(self, user_elem, set_name):
        profile = self.get_xml_setting(user_elem, set_name)
        if profile:
            work = int(profile.find('work').text)
            shortbreak = int(profile.find('shortbreak').text)
            longbreak = int(profile.find('longbreak').text)
            cycle = int(profile.find('cycle').text)
            return Setting(set_name, work, shortbreak, longbreak, cycle)
        return None

    def get_xml_setting(self, user_elem, set_name):
        settings = {setting.find('name').text: setting for setting in user_elem.findall('setting')} # noqa
        return settings[set_name]

    def get_user(self, name, setting):
        users = self.load_xml()
        if name not in users:
            return False
        else:
            return self.user_constructor(users[name], setting)

import xml.etree.ElementTree as ET
from user import User
from setting import Profile


class XmlORM(object):
    def __init__(self, path_to_db):
        self.type = 'xml'
        self.path_to_db = path_to_db
        self.create_db()
        self.tree = ET.parse(self.path_to_db)

    def create_db(self):
        try:
            with open(self.path_to_db, 'r'):
                pass
        except FileNotFoundError: # noqa
            with open(self.path_to_db, 'w'):
                ET.ElementTree(ET.Element('users')).write(self.path_to_db)

    def delete_user(self, name):
        users = self.load_xml()
        if name in users:
            users[name].remove()
            self.tree.write(self.path_to_db)
            return True
        return False

    def update_user(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_xml()
        if name in users:
            user_elem = users[name]
            profile = self.profile_xml(user_elem, pr_name)
            if profile:
                self.update_profile(user_elem, profile, work, shortbreak, longbreak, cycle)
                self.tree.write(self.path_to_db)
            return True
        return False

    def update_profile(self, user_elem, profile, work, shortbreak, longbreak, cycle):
        print(f'work::{work}')
        profile.find('work').text = str(work) or profile.find('work')
        profile.find('shortbreak').text = str(shortbreak) or profile.find('shortbreak')
        profile.find('longbreak').text = str(longbreak) or profile.find('longbreak')
        profile.find('cycle').text = str(cycle) or profile.find('cycle')

    def create_user(self, name, pr_name, shortbreak, longbreak, cycle):
        users = self.load_xml()
        if name in users:
            return False
        else:
            self.user_xml(name, pr_name, shortbreak, longbreak, cycle)
        return True

    def user_xml(self, name, pr_name, shortbreak, longbreak, cycle):
        root = self.tree.getroot()

        usr = ET.Element('user')
        name = ET.SubElement(usr, 'name')
        name.text = name

        profile = ET.SubElement(usr, 'profile')
        set_name = ET.SubElement(profile, 'name')
        set_name.text = pr_name

        work = ET.SubElement(profile, 'work')
        work.text = str(work)

        shortbreak = ET.SubElement(profile, 'shortbreak')
        shortbreak.text = str(shortbreak)

        longbreak = ET.SubElement(profile, 'longbreak')
        longbreak.text = str(longbreak)

        cycle = ET.SubElement(profile, 'cycle')
        cycle.text = str(cycle)

        root.append(usr)
        self.tree.write(self.path_to_db)

    def load_xml(self):
        return {user.find('name').text: user for user in self.tree.getroot()}

    def make_user(self, user_elem, pr_name):
        profile = self.make_profile(user_elem, pr_name)
        if profile:
            name = user_elem.find('name').text
            return User(None, name, profile)

    def make_profile(self, user_elem, pr_name):
        profile = self.profile_xml(user_elem, pr_name)
        if profile:
            work = int(profile.find('work').text)
            shortbreak = int(profile.find('shortbreak').text)
            longbreak = int(profile.find('longbreak').text)
            cycle = int(profile.find('cycle').text)
            return Profile(pr_name, work, shortbreak, longbreak, cycle)
        return None

    def profile_xml(self, user_elem, pr_name):
        profiles = {profile.find('name').text: profile for profile in user_elem.findall('profile')}
        if pr_name in profiles:
            return profiles[pr_name]
        return None

    def get_user(self, name, pr_name):
        users = self.load_xml()
        if name not in users:
            return False
        else:
            return self.make_user(users[name], pr_name)

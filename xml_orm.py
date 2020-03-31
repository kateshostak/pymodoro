import xml.etree.ElementTree as ET
from user import User
from setting import Profile


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
            with open(self.path_to_db, 'w'):
                ET.ElementTree(ET.Element('users')).write(self.path_to_db)

    def delete_user(self, user):
        user = self.get_user(self, user)

    def udate_user(self, user):
        users = self.load_xml()
        if user.name in users:
            user_elem = users[user.name]
            profile = self.get_xml_profile(user_elem, user.profile)
            if profile:
                self.update_profile(user, user_elem, profile)
            return True
        return False

    def upadate_profile(self, user, user_elem, profile):
        profile.find('work').text = str(user.work) or profile.find('work')
        profile.find('shortbreak').text = str(user.shortbreak) or profile.find('shortbreak')
        profile.find('lonbreak').text = str(user.longbreak) or profile.find('longbreak')
        profile.find('cycle').text = str(user.cycle) or profile.find('cycle')

    def create_user(self, user):
        users = self.load_xml()
        if user.name in users:
            return False
        else:
            self.user_xml(user)
        return True

    def user_xml(self, user):
        tree = ET.parse(self.path_to_db)
        root = tree.getroot()

        usr = ET.Element('user')
        name = ET.SubElement(usr, 'name')
        name.text = user.name

        profile = ET.SubElement(usr, 'profile')
        set_name = ET.SubElement(profile, 'name')
        set_name.text = user.profile

        work = ET.SubElement(profile, 'work')
        work.text = str(user.work)

        shortbreak = ET.SubElement(profile, 'shortbreak')
        shortbreak.text = str(user.shortbreak)

        longbreak = ET.SubElement(profile, 'longbreak')
        longbreak.text = str(user.longbreak)

        cycle = ET.SubElement(profile, 'cycle')
        cycle.text = str(user.cycle)

        root.append(usr)
        tree.write(self.path_to_db)

    def load_xml(self):
        users = ET.parse(self.path_to_db).getroot()
        return {user.find('name').text: user for user in users}

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

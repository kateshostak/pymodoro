import pdb
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

    def record_pomodoro(self, name, pr_name, start_time, duration):
        users = self.load_xml()
        if name in users:
            stats = users[name].find('statistics')
            stats.append(self.build_stats_xml(pr_name, start_time, duration))
            self.tree.write(self.path_to_db)

    def delete_user(self, name):
        users = self.load_xml()
        if name in users:
            self.tree.getroot().remove(users[name])
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

    def add_profile(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_xml()
        if name in users:
            users[name].append(self.build_xml_stats)

    def update_profile(self, user_elem, profile, work, shortbreak, longbreak, cycle):
        profile.find('work').text = str(work) or profile.find('work').text
        profile.find('shortbreak').text = str(shortbreak) or profile.find('shortbreak').text
        profile.find('longbreak').text = str(longbreak) or profile.find('longbreak').text
        profile.find('cycle').text = str(cycle) or profile.find('cycle').text

    def create_user(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_xml()
        if name in users:
            return False
        self.build_user_xml(name, pr_name, work, shortbreak, longbreak, cycle)
        return True

    def build_user_xml(self, name, pr_name, work, shortbreak, longbreak, cycle):
        root = self.tree.getroot()
        usr = ET.Element('user')
        ET.SubElement(usr, 'name').text = name
        ET.SubElement(usr, 'settings').append(self.build_profile_xml(pr_name, work, shortbreak, longbreak, cycle))
        ET.SubElement(usr, 'statistics')
        root.append(usr)
        self.tree.write(self.path_to_db)

    def build_stats_xml(self, pr_name, start_time, duration):
        data = ET.Element('data')
        ET.SubElement(data, 'name').text = pr_name
        ET.SubElement(data, 'timestamp').text = str(start_time)
        ET.SubElement(data, 'duration').text = str(duration)
        return data

    def build_profile_xml(self, pr_name, work, shortbreak, longbreak, cycle):
        profile = ET.Element('profile')
        ET.SubElement(profile, 'name').text = pr_name
        ET.SubElement(profile, 'work').text = str(work)
        ET.SubElement(profile, 'shortbreak').text = str(shortbreak)
        ET.SubElement(profile, 'longbreak').text = str(longbreak)
        ET.SubElement(profile, 'cycle').text = str(cycle)
        return profile

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
        profiles = {profile.find('name').text: profile for profile in user_elem.find('settings')}
        if pr_name in profiles:
            return profiles[pr_name]
        return None

    def get_user(self, name, pr_name):
        users = self.load_xml()
        if name not in users:
            return False
        else:
            return self.make_user(users[name], pr_name)

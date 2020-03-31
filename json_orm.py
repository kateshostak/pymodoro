import json
from user import User
from setting import Profile


class JsonORM(object):
    def __init__(self, path_to_file):
        self.type = 'json'
        self.path_to_file = path_to_file
        self.create_db()

    def create_db(self):
        try:
            with open(self.path_to_file, 'r'):
                pass
        except FileNotFoundError:  # noqa
            with open(self.path_to_file, 'w'):
                pass

    def write_json(self, data):
        with open(self.path_to_file, 'w') as fp:
            json.dump(data, fp)

    def load_json(self):
        with open(self.path_to_file, 'r') as fp:
            try:
                return json.load(fp)
            except ValueError:
                return dict()

    def get_user(self, name, setting):
        users_dict = self.load_json()
        if name in users_dict:
            user = users_dict[name]
            profile = self.get_profile(user, setting)
            if profile:
                setting = Setting(setting, profile['work'], profile['shortbreak'], profile['longbreak'], profile['cycle'])
                return User(None, name, setting)
        return None

    def get_profile(self, user, setting):
        if setting in user:
            return user[setting]
        return None

    def create_user(self, name, setting, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            return False
        profile = self.create_profile(setting, work, shortbreak, longbreak, cycle)
        new_user = {
                setting: profile,
                'statistics': []
                }
        users = self.load_json()
        users[name] = new_user
        self.write_json(users)
        return True

    def create_profile(self, setting, work, shortbreak, longbreak, cycle):
        profile = {
                'setting': setting,
                'work': work,
                'shortbreak': shortbreak,
                'longbreak': longbreak,
                'cycle': cycle
                }
        return profile

    def update_user(self, name, setting, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            updated = self.update_profile(users[name], setting, work, shortbreak, longbreak, cycle)
            if updated:
                self.write_json(users)
                return True
        return False

    def update_profile(self, user, setting, work, shortbreak, longbreak, cycle):
        profile = self.get_profile(user, setting)
        if profile:
            profile['work'] = work or profile['work']
            profile['shortbreak'] = shortbreak or profile['shortbreak']
            profile['longbreak'] = longbreak or profile['longbreak']
            profile['cycle'] = cycle or profile['cycle']
            return True
        return False

    def add_profile(self, name, setting, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if setting in users[name]:
            return False
        profile = self.create_profile(setting, work, shortbreak, longbreak, cycle)
        users[name][setting] = profile
        self.write_json(users)
        return True

    def delete_profile(self, name, setting):
        users = self.load_json()
        if name in users:
            if setting in users[name] and len(users[name]) > 2:
                users[name].pop(setting)
                self.write_json(users)
                return True
        return False

    def delete_user(self, name):
        users = self.load_json()
        if name in users:
            users.pop(name)
            self.write_json(users)
            return True
        return False

    def record_pomodoro(self, name, setting, work, start_time):
        users = self.load_json()
        stats = self.stats_dict(setting, work, start_time)
        users[name]['statistics'].append(stats)
        self.write_json(users)

    def stats_dict(self, setting, work, start_time):
        stats = {
                'setting': setting,
                'start_time': start_time,
                'work_time': work
                }
        return stats

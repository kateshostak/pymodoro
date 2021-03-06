import pdb
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

    def get_user(self, name, pr_name):
        users_dict = self.load_json()
        if name in users_dict:
            user = users_dict[name]
            pr = self.get_profile(user, pr_name)
            if pr:
                pr_name = Profile(pr_name, pr['work'], pr['shortbreak'], pr['longbreak'], pr['cycle'])
                return User(None, name, pr_name)
        return None

    def get_profile(self, user, pr_name):
        if pr_name in user['settings']:
            return user['settings'][pr_name]
        return None

    def create_user(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            return False
        profile = self.create_profile(work, shortbreak, longbreak, cycle)
        new_user = {
                'settings': {pr_name: profile},
                'statistics': []
                }
        users = self.load_json()
        users[name] = new_user
        self.write_json(users)
        return True

    def create_profile(self, work, shortbreak, longbreak, cycle):
        profile = {
                'work': work,
                'shortbreak': shortbreak,
                'longbreak': longbreak,
                'cycle': cycle
                }
        return profile

    def update_user(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            updated = self.update_profile(users[name], pr_name, work, shortbreak, longbreak, cycle)
            if updated:
                self.write_json(users)
                return True
        return False

    def update_profile(self, user, pr_name, work, shortbreak, longbreak, cycle):
        profile = self.get_profile(user, pr_name)
        if profile:
            profile['work'] = work or profile['work']
            profile['shortbreak'] = shortbreak or profile['shortbreak']
            profile['longbreak'] = longbreak or profile['longbreak']
            profile['cycle'] = cycle or profile['cycle']
            return True
        return False

    def add_profile(self, name, pr_name, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if pr_name in users[name]['settings']:
            return False
        profile = self.create_profile(work, shortbreak, longbreak, cycle)
        users[name]['settings'][pr_name] = profile
        self.write_json(users)
        return True

    def delete_profile(self, name, pr_name):
        users = self.load_json()
        if name in users:
            if pr_name in users[name]['settings'] and len(users[name]['settings']) > 1:
                users[name]['settings'].pop(pr_name)
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

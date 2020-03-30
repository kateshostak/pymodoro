import json
from user import User


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
            return User(None, name, user['work'], user['shortbreak'], user['longbreak'], user['cycle'])
        else:
            return None

    def create_user(self, name, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            return False
        new_user = {
                'work': work,
                'shortbreak': shortbreak,
                'longbreak': longbreak,
                'cycle': cycle,
                'statistics': []
                }
        users = self.load_json()
        users[name] = new_user
        self.write_json(users)
        return True

    def update_user(self, name, work, shortbreak, longbreak, cycle):
        users = self.load_json()
        if name in users:
            self.update_json(users, name, work, shortbreak, longbreak, cycle)
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

    def update_json(self, users, name, work, shortbreak, longbreak, cycle):
        user = users[name]
        user['work'] = work or user['work']
        user['shortbreak'] = shortbreak or user['shortbreak']
        user['longbreak'] = longbreak or user['longbreak']
        user['cycle'] = cycle or user['cycle']

    def record_pomodoro(self, name, work, start_time):
        users = self.load_json()
        stats = self.stats_dict(work, start_time)
        users[name]['statistics'].append(stats)
        self.write_json(users)

    def stats_dict(self, work, start_time):
        stats = {
                'start_time': start_time,
                'work_time': work
                }
        return stats

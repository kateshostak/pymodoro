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

    def create_user(self, user):
        new_user = {
                'work': user.work,
                'shortbreak': user.shortbreak,
                'longbreak': user.longbreak,
                'cycle': user.cycle,
                'statistics': []
                }
        users = self.load_json()
        users[user.name] = new_user
        self.write_json(users)

    def update_user(self, user):
        users = self.load_json()
        self.update_json(users, user)
        self.write_json(users)

    def delete_user(self, name):
        users = self.load_json()
        if name in users:
            users.pop(name)
            self.write_json(users)
            return True
        return False

    def update_json(self, users, user_profile):
        name = user_profile.name
        user = users[name]
        users[name]['work'] = user_profile.work or user['work']
        users[name]['shortbreak'] = user_profile.shortbreak or user['shortbreak']
        users[name]['longbreak'] = user_profile.longbreak or user['longbreak']
        users[name]['cycle'] = user_profile.cycle or user['cycle']

    def record_pomodoro(self, user_profile, start_time):
        users = self.load_json()
        stats = self.stats_dict(user_profile, start_time)
        users[user_profile.name]['statistics'].append(stats)
        self.write_json(users)

    def stats_dict(self, user_profile, start_time):
        stats = {
                'start_time': start_time,
                'work_time': user_profile.work
                }
        return stats

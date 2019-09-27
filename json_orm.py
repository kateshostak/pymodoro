import json

from user import User


class JsonORM(object):
    def __init__(self, path_to_file):
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
                return list()

    def make_dict(self):
        users = self.load_json()
        users_dict = {}
        for user in users:
            users_dict = {
                    user['name']: User(
                        None,
                        user['name'],
                        user['work_time'],
                        user['short_break'],
                        user['long_break'],
                        user['cycle']
                        )
                    }
        return users_dict

    def get_user(self, name):
        users_dict = self.make_dict()
        if name in users_dict:
            return users_dict[name]
        else:
            return None

    def create_user(self, user_profile):
        new_user = {
                'name': user_profile.name,
                'work_time': user_profile.work_time,
                'short_break': user_profile.short_break,
                'long_break': user_profile.long_break,
                'cycle': user_profile.cycle,
                'statistics': []
                }
        users = self.load_json()
        users.append(new_user)
        self.write_json(users)
        return self.get_user(user_profile.name)

    def update_user(self, user_profile):
        users = self.load_json()
        self.update_json(users, user_profile)
        self.write_json(users)
        return self.get_user(user_profile.name)

    def update_json(self, users, user_profile):
        for user in users:
            if user['name'] == user_profile.name:
                user['work_time'] = user_profile.work_time
                user['short_break'] = user_profile.short_break
                user['long_break'] = user_profile.long_break
                user['cycle'] = user_profile.cycle

    def record_pomodoro(self, user_profile, start_time):
        users = self.load_json()
        stats = self.stats_dict(user_profile, start_time)
        for user in users:
            if user['name'] == user_profile.name:
                user['statistics'].append(stats)

        self.write_json(users)

    def stats_dict(self, user_profile, start_time):
        stats = {
                'start_time': start_time,
                'work_time': user_profile.work_time
                }
        return stats

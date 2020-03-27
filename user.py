class User():

    def __init__(self, id_, name, setting):
        self.id = id_
        self.name = name
        self.setting = setting

    def __str__(self):
        user_str = f'id::{self.id}, name::{self.name}' # noqa
        return user_str + str(self.setting)

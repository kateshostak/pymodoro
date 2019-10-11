class User(object):

    def __init__(self, id_, name, work, shortbreak, longbreak, cycle):
        self.id = id_
        self.name = name
        self.work= work
        self.shortbreak = shortbreak
        self.longbreak = longbreak
        self.cycle = cycle

    def __str__(self):
        user_str = f'id::{self.id}, name::{self.name}'
        return user_str

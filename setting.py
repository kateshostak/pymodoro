class Setting():
    def __init__(self, name, work, shortbreak, longbreak, cycle):
        self.name = name
        self.work = work
        self.shortbreak = shortbreak
        self.longbreak = longbreak
        self.cycle = cycle

    def __str__(self):
        return f'Setting::{self.name}, work::{slf.work}, shortbreak::{self.shortbreak}, longbreak::{self.longbreak}, cycle::{self.cycle}' # noqa

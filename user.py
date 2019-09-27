class User(object):

    def __init__(self, uid, name, work_time, short_break, long_break, cycle):
        self.id = uid
        self.name = name
        self.work_time = work_time
        self.short_break = short_break
        self.long_break = long_break
        self.cycle = cycle

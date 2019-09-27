import sqlite3

from user import User


class SqliteORM(object):

    def __init__(self, path_to_db):
        self.conn = sqlite3.connect(path_to_db)
        self.cur = self.conn.cursor()
        self.create_db()

    def create_db(self):
        self.cur.execute("pragma foreign_keys = 1")

        self.cur.execute("""create table if not exists users (
                   id integer primary key,
                   name char(50) unique not null,
                   work int default(25),
                   short_break int default(5),
                   long_break int default(15),
                   cycle int default(4))""")

        self.cur.execute("""create table if not exists stats (
                           id integer,
                           start_time float,
                           work integer,
                           foreign key(id) references users(id)
                           )""")

    def get_user(self, name):
        user = self.cur.execute(
                """select * from users where name=?""",
                (name,)
                ).fetchone()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4], user[5])
        return None

    def create_user(self, user_profile):
        self.cur.execute(
                """insert into users(
                name,
                work,
                short_break,
                long_break,
                cycle)
                values(?, ?, ?, ?, ?)""",
                (
                    user_profile.name,
                    user_profile.work_time,
                    user_profile.short_break,
                    user_profile.long_break,
                    user_profile.cycle
                    )
        )
        self.commit()
        return self.get_user(user_profile.name)

    def update_user(self, user_profile):
        self.cur.execute(
            """update users set
            work=?,
            short_break=?,
            long_break=?,
            cycle=?
            where name=? """,
            (
                user_profile.work_time,
                user_profile.short_break,
                user_profile.long_break,
                user_profile.cycle,
                user_profile.name
                )
        )
        self.commit()
        return self.get_user(user_profile.name)

    def record_pomodoro(self, user_profile, start_time):
        self.cur.execute(
            """insert into stats(id, start_time, work) values(?, ?, ?)""",
            (user_profile.id, start_time, user_profile.work_time)
        )
        self.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

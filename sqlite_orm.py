import sqlite3

from user import User


class SqliteORM(object):

    def __init__(self, path_to_db):
        self.type = 'sqlite'
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

    def get_user(self, name, setting):
        user = self.cur.execute(
                """select * from users where name=?""",
                (name,)
                ).fetchone()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4], user[5])
        return None

    def create_user(self, user_profile):
        self.cur.execute(
                """
                insert into users(
                name,
                work,
                short_break,
                long_break,
                cycle)
                values(?, ?, ?, ?, ?)
                """,
                (
                    user_profile.name,
                    user_profile.work,
                    user_profile.shortbreak,
                    user_profile.longbreak,
                    user_profile.cycle
                    )
        )
        self.commit()

    def update_user(self, user_profile):
        self.cur.execute(
            """
            update users set
            work=coalesce(?, work),
            short_break=coalesce(?, short_break),
            long_break=coalesce(?, long_break),
            cycle=coalesce(?, cycle)
            where name=?
            """,
            (
                user_profile.work,
                user_profile.shortbreak,
                user_profile.longbreak,
                user_profile.cycle,
                user_profile.name
                )
        )
        self.commit()

    def delete_user(self, name):
        user_id = self.get_user(name, 0).id
        self.cur.execute("delete from stats where id=?",(user_id,))
        self.cur.execute("delete from users where name=?",(name,))
        self.commit()


    def record_pomodoro(self, user, start_time):
        self.cur.execute(
            """insert into stats(id, start_time, work) values(?, ?, ?)""",
            (user.id, start_time, user.work)
        )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


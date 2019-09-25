#!/usr/bin/python3 -tt

import sys
import subprocess
import time
import asyncio
import sqlite3
import argparse
import json
from collections import namedtuple


class ORM(object):
    SQLITE = 'sqlite'
    JSON = 'json'

    def __init__(self, db_type, path_to_db):
        self.db_types = {
                ORM.SQLITE: ORM_sqlite,
                ORM.JSON: ORM_json
                }
        self.db_type = db_type
        self.path_to_db = path_to_db

    def get_db(self):
        return self.db_types[self.db_type](self.path_to_db)


class ORM_json(object):
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.create_db()

    def create_db(self):
        try:
            with open(self.path_to_file, 'r'):
                pass
        except FileNotFoundError:
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

class ORM_sqlite(object):

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
        self.cur.execute("""insert into stats(id, start_time, work) values(?, ?, ?)""", (user_profile.id, start_time, user_profile.work_time))
        self.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class User(object):

    def __init__(self, uid, name, work_time, short_break, long_break, cycle):
        self.id = uid
        self.name = name
        self.work_time = work_time
        self.short_break = short_break
        self.long_break = long_break
        self.cycle = cycle


class Ticker(object):

    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.is_paused = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    async def run(self, secs):
        sec = secs
        while sec >= 0:
            await asyncio.sleep(self.interval)
            if self.is_paused:
                continue
            self.callback(sec)
            sec -= 1


class Pomodoro(object):
    WORK = 'work'
    BREAK = 'break'
    LONG_BREAK = 'long_break'

    def __init__(self, user, db):
        self.user = user
        self.db = db

        self.durations = {
            Pomodoro.WORK: self.user.work_time,
            Pomodoro.BREAK: self.user.short_break,
            Pomodoro.LONG_BREAK: self.user.long_break,
        }

        self.notifications = {
            Pomodoro.WORK: "Work!",
            Pomodoro.BREAK: "Break!",
            Pomodoro.LONG_BREAK: "Long break!",
        }

        self.current_ticker = None
        self.current_activity = None
        self.current_counter = 0
        self.cycle_len = self.user.cycle
        self.is_paused = False

    def next(self):
        if self.current_activity == Pomodoro.WORK:
            self.current_counter += 1
            if self.current_counter == self.cycle_len:
                self.current_activity = Pomodoro.LONG_BREAK
                self.current_counter = 0
            else:
                self.current_activity = Pomodoro.BREAK
            return self.current_activity
        else:
            self.current_activity = Pomodoro.WORK
            return self.current_activity

    async def start(self):
        while True:
            activity = self.next()
            start_time = time.time()
            await self.start_activity(activity)
            if self.current_activity == Pomodoro.WORK:
                self.db.record_pomodoro(self.user, start_time)

    async def start_activity(self, activity):
        self.show_notification(self.notifications[activity])
        await self.run_activity(self.durations[activity])

    async def run_activity(self, secs):
        def tick(sec):
            seconds = sec % 60
            minutes = (sec // 60) % 60
            hours = sec // 3600
            print(f'{hours:02d}:{minutes:02d}:{seconds:02d}', end='\r')

        self.current_ticker = Ticker(1, tick)
        await self.current_ticker.run(secs)

    def show_notification(self, text):
        print(text)
        subprocess.run([
            "osascript", "-e", "display notification \"%s\" with title \"PyModoro\" sound name \"Submarine\"" % text
        ])

    def toggle_pause(self):
        print('paused' if not self.is_paused else 'work')
        self.is_paused = not self.is_paused

        self.current_ticker.toggle_pause()


def user_input(q, pomodoro):
    asyncio.ensure_future(q.put(sys.stdin.readline()))
    pomodoro.toggle_pause()


class Parser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                prog='Pymodoro',
                description='Simple timer for Pomodoro Technique',
                usage='%(prog)s name -p [work_time, short_break, long_break,cycle]'
                )
        self.parser.add_argument('name', help='Name of the pomodoro user', action='store')
        self.parser.add_argument(
                '-p',
                '--profile',
                metavar=('work_time', 'short_break', 'long_break', 'cycle'),
                nargs=4,
                type=int,
                action='store'
                )

    def parse_args(self):
        return self.parser.parse_args()

def main():
    Profile = namedtuple(
            'Profile',
            [
                'name',
                'work_time',
                'short_break',
                'long_break',
                'cycle',
                'update'
                ],
            defaults=[
                None,
                25*60,
                5*60,
                10*60,
                4,
                False
                ]
            )
    parser = Parser()
    args = parser.parse_args()
    if args.profile:
        user_profile = Profile(
                name=args.name,
                work_time=args.profile[0]*60,
                short_break=args.profile[1]*60,
                long_break=args.profile[2]*60,
                cycle=args.profile[3],
                update=True
                )
    else:
        user_profile = Profile(args.name)

    orm = ORM('json', 'data.json')
    #orm = ORM('sqlite', 'pom.db')
    db = orm.get_db()
    user = db.get_user(user_profile.name)
    if not user:
        user = db.create_user(user_profile)
    elif user_profile.update:
        user = db.update_user(user_profile)

    pomodoro = Pomodoro(user, db)
    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.add_reader(sys.stdin, user_input, q, pomodoro)

    loop.run_until_complete(pomodoro.start())

if __name__ == '__main__':
    main()

#!/usr/bin/python3 -tt

import sys
import subprocess
import time
import asyncio
import sqlite3
import argparse
from collections import namedtuple

class ORM(object):

    def __init__(self, path_to_db='pom.db'):
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

    def get_user(self, user_profile):
        user = self.cur.execute("""select * from users where name=?""", (user_profile.name,)).fetchone()
        if user:
            return User(user)
        return None

    def create_user(self, user_profile):
        self.cur.execute(
                """insert into users(name, work, short_break, long_break, cycle) values(?, ?, ?, ?, ?)""",
                (user_profile.name, user_profile.work_time, user_profile.short_break, user_profile.long_break, user_profile.cycle)
        )
        self.commit()
        return self.get_user(user_profile)

    def update_user(self, user_profile):
        self.cur.execute(
            """update users set work=?, short_break=?, long_break=?, cycle=? where name=? """,
                (
                    user_profile.work_time,
                    user_profile.short_break,
                    user_profile.long_break,
                    user_profile.cycle,
                    user_profile.name)
        )
        self.commit()
        return self.get_user(user_profile)

    def record_pomodoro(self, user_profile, start_time):
        self.cur.execute("""insert into stats(id, start_time, work) values(?, ?, ?)""", (user_profile.id, start_time, user_profile.work))
        self.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class User(object):
    def __init__(self, params):
        self.id, self.name, self.work, self.short_break, self.long_break, self.cycle = params

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

    def __init__(self, user, orm):
        self.user = user
        self.orm = orm

        self.durations = {
            Pomodoro.WORK: self.user.work,
            Pomodoro.BREAK: self.user.short_break,
            Pomodoro.LONG_BREAK:self.user.long_break,
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
                self.orm.record_pomodoro(self.user, start_time)

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
    Profile = namedtuple('Profile',['name', 'work_time', 'short_break', 'long_break', 'cycle', 'update'], defaults=[None, 25, 5, 10, 4, False])
    parser = Parser()
    args = parser.parse_args()
    if args.profile:
        user_profile = Profile(
                name=args.name,
                work_time=args.profile[0],
                short_break=args.profile[1],
                long_break=args.profile[2],
                cycle=args.profile[3],
                update=True
                )
    else:
        user_profile = Profile(args.name)

    orm = ORM()
    user = orm.get_user(user_profile)
    if not user:
        user = orm.create_user(user_profile)
    if user_profile.update:
        user = orm.update_user(user_profile)

    pomodoro = Pomodoro(user, orm)
    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.add_reader(sys.stdin, user_input, q, pomodoro)

    loop.run_until_complete(pomodoro.start())

if __name__ == '__main__':
    main()

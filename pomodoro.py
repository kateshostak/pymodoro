#!/usr/bin/python3 -tt

import sys
import subprocess
import time
import asyncio
import sqlite3
from collections import namedtuple

class ORM(object):

    def __init__(self, path_to_db):
        self.conn = self.connect_db(path_to_db)
        self.cur = self.conn.cursor()
        self.create_db()

    def connect_db(self, path_to_db):
            return sqlite3.connect(path_to_db)

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
                           id integer primary key,
                           start_focus float,
                           end_focus float,
                           foreign key(id) references users(id)
                           )""")

    def get_user(self, user_profile):
        usr = self.create_user(user_profile)
        return User(usr)

    def create_user(self, user_profile):
        try:
            self.cur.execute("""insert into users(name) values(?)""", [user_profile.name])
        except Exception as e:
            print("User already exists")

        usr = self.cur.execute("""select * from users where name=?""", [user_profile.name]).fetchone()
        return usr

    def update_user(self, user_profile):
        self.cur.execute("""update users set work=?, short_break=?, long_break=?, cycle=? """, user_profile[1:])

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class User(object):
    def __init__(self, params):
        self.uid, self.name, self.work, self.short_break, self.long_break, self.cycle = params

class Ticker(object):

    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.is_paused = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    async def run(self, secs):
        sec = 0
        while sec < secs:
            await asyncio.sleep(self.interval)
            if self.is_paused:
                continue
            self.callback(sec)
            sec += 1


class Pomodoro(object):

    WORK = 'work'
    BREAK = 'break'
    LONG_BREAK = 'long_break'

    def __init__(self, user):
        self.durations = {
            Pomodoro.WORK: user.work,
            Pomodoro.BREAK: user.short_break,
            Pomodoro.LONG_BREAK:user.long_break,
        }

        self.notifications = {
            Pomodoro.WORK: "Work!",
            Pomodoro.BREAK: "Break!",
            Pomodoro.LONG_BREAK: "Long break!",
        }

        self.current_ticker = None

        self.cycle_len = user.cycle
        self.is_paused = False

    async def start(self):
        while True:
#            activity = self.next()
#            await self.start_activity(activity)

            for i in range(self.cycle_len):
                 await self.start_activity(Pomodoro.WORK)
                 if i != self.cycle_len - 1:
                     await self.start_activity(Pomodoro.BREAK)
                 else:
                     await self.start_activity(Pomodoro.LONG_BREAK)

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
            "osascript", "-e", "display notification \"%s\"" % text
        ])

    def toggle_pause(self):
        print('paused' if not self.is_paused else 'work')
        self.is_paused = not self.is_paused

        self.current_ticker.toggle_pause()


def user_input(q, pomodoro):
    asyncio.ensure_future(q.put(sys.stdin.readline()))
    pomodoro.toggle_pause()


def main():
    # parse args

    # pomodoro with args
    uprofile = namedtuple('Profile',['name', 'work_time', 'short_break', 'long_break', 'cycle_len'])
    user_profile = uprofile('alice', 10, 10, 10, 10)
    orm = ORM('pom.db')
    user = orm.get_user(user_profile)
    pomodoro = Pomodoro(user)
    orm.commit()
    orm.close()
    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.add_reader(sys.stdin, user_input, q, pomodoro)

    loop.run_until_complete(pomodoro.start())


if __name__ == '__main__':
    main()

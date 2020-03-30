import sys
import subprocess
import time
import asyncio
import argparse
from collections import namedtuple

from user import User
from orm import ORM
from arguments_parser import ArgParser


class Ticker(object):

    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.is_paused = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    async def run(self, secs):  # noqa
        sec = secs
        while sec >= 0:
            await asyncio.sleep(self.interval)
            if self.is_paused:
                continue
            self.callback(sec)
            sec -= 1


# class ActivityManager
#
class Pomodoro(object):
    WORK = 'work'
    BREAK = 'break'
    LONG_BREAK = 'long_break'

    def __init__(self, user, orm):
        self.user = user
        self.orm = orm

        self.durations = {
            Pomodoro.WORK: self.user.setting.work,
            Pomodoro.BREAK: self.user.setting.shortbreak,
            Pomodoro.LONG_BREAK: self.user.setting.longbreak,
        }

        self.notifications = {
            Pomodoro.WORK: "Work!",
            Pomodoro.BREAK: "Break!",
            Pomodoro.LONG_BREAK: "Long break!",
        }

        self.current_ticker = None
        self.current_activity = None
        self.current_counter = 0
        self.cycle_len = self.user.setting.cycle
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
                self.orm.record_pomodoro(self.user.name, self.user.setting.name, self.user.setting.work, start_time) # noqa

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
            "osascript", "-e", "display notification \"%s\" with title \"PyModoro\" sound name \"Submarine\"" % text # noqa
        ])

    def toggle_pause(self):
        print('paused' if not self.is_paused else 'work')
        self.is_paused = not self.is_paused

        self.current_ticker.toggle_pause()


class PymodoroManager():
    RUN = 'run'
    NEW = 'new'
    ADD = 'add'
    DELETE = 'delete'
    UPDATE = 'update'

    def __init__(self):
        self.argparser = ArgParser()
        self.command, self.args = self.argparser.parse_args()
        self.orm = ORM.get_orm(ORM.SQLITE, 'new_pom.db')
        self.orm = ORM.get_orm(ORM.JSON, 'data.json')
        # self.orm = ORM.get_orm(ORM.XML, 'data.xml')
        self.command_to_func = {
                PymodoroManager.RUN: self.start_pymodoro,
                PymodoroManager.NEW: self.create_user,
                PymodoroManager.ADD: self.add_profile,
                PymodoroManager.UPDATE: self.update_user,
                PymodoroManager.DELETE: self.delete_user
        }
        self.loop = asyncio.get_event_loop()
        self.q = asyncio.Queue()

    def start(self, *args, **kwargs):
        self.command_to_func[self.command](*args, **kwargs)

    def start_pymodoro(self):
        user = self.orm.get_user(self.args.name, self.args.setting)
        if not user:
            print(f'No user with name {self.args.name} was found')
        else:
            pomodoro = Pomodoro(user, self.orm)
            self.loop.add_reader(sys.stdin, user_input, self.q, pomodoro)
            self.loop.run_until_complete(pomodoro.start())

    def create_user(self):
        res = self.orm.create_user(self.args.name, self.args.setting, self.args.work, self.args.shortbreak, self.args.longbreak, self.args.cycle) # noqa
        if res:
            print(f'User {self.args.name} was created')
        else:
            print(f'The user with name {self.args.name} already exists')

    def update_user(self):
        res = self.orm.update_user(self.args.name, self.args.setting, self.args.work, self.args.shortbreak, self.args.longbreak, self.args.cycle) # noqa
        if res:
            print(f'User {self.args.name} was updated')
        else:
            print(f'No user with name {self.args.name} was found ')

    def add_profile(self):
        res = self.orm.add_profile(self.args.name, self.args.setting, self.args.work, self.args.shortbreak, self.args.longbreak, self.args.cycle) # noqa
        if res:
            print(f'Setting {self.args.setting} was added to user {self.args.name}')
        else:
            print(f'User setting with name {self.args.setting} already exists')

    def delete_user(self):
        res = self.orm.delete_user(self.args.name)
        if res:
            print(f'User {self.args.name} was deleted')
        else:
            print(f'No user with name {self.args.name} was found')


def user_input(q, pomodoro):
    asyncio.ensure_future(q.put(sys.stdin.readline()))
    pomodoro.toggle_pause()


def main():
    manager = PymodoroManager()
    manager.start()
    # parser = Parser()
    # common_options, command, command_options = parser.parse()
    #
    # CREATE DEPS (such as orm) FOR SUPERCLASS FROM common_options
    #
    # superclass = SUPERCLASS(common_options)
    #
    # if command == "new" (COMMAND_NEW):
    #       superclass.handle_new_user(command_options)
    #
    # if command == "run":
    #       superclass.handle_run(command_options)

    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)


if __name__ == '__main__':
    main()

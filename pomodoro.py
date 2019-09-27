import sys
import subprocess
import time
import asyncio
import argparse
from collections import namedtuple

from user import User
from orm import ORM


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

    # orm = ORM(ORM.JSON, 'data.json')
    #orm = ORM('sqlite', 'pom.orm')
    # orm = orm.get_orm()

    orm = ORM.get_orm(ORM.JSON, 'data.json')
    user = orm.get_user(user_profile.name)
    if not user:
        user = orm.create_user(user_profile)
    elif user_profile.update:
        user = orm.update_user(user_profile)

    pomodoro = Pomodoro(user, orm)
    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.add_reader(sys.stdin, user_input, q, pomodoro)

    loop.run_until_complete(pomodoro.start())

#!/usr/bin/python3 -tt

import sys
import subprocess
import time
import asyncio
import sqlite3


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

    def __init__(
        self, work_time, short_break, long_break, cycle_len
    ):
        self.durations = {
            Pomodoro.WORK: work_time,
            Pomodoro.BREAK: short_break,
            Pomodoro.LONG_BREAK: long_break,
        }

        self.notifications = {
            Pomodoro.WORK: "Work!",
            Pomodoro.BREAK: "Break!",
            Pomodoro.LONG_BREAK: "Long break!",
        }

        self.current_ticker = None

        self.cycle_len = cycle_len
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


        # sec = 0
        # while True:
        #     await asyncio.sleep(1)
        #     if self.is_paused:
        #         continue
        #     else:
        #         if sec < secs:
        #             seconds = sec % 60
        #             minutes = (sec // 60) % 60
        #             hours = (sec)//3600
        #             print(f'{hours:02d}:{minutes:02d}:{seconds:02d}', end='\r')
        #             sec += 1
        #         else:
        #             break

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
    # work_time = int(input('Set the work time in minutes: ').strip())
    # short_break = int(input('Set the short rest time in minutes: ').strip())
    # long_break = int(input('Set the long break time in minutes: ').strip())
    # cycle_len = int(input('Set the long break frequency in minutes: ').strip())
    # pomodoro = Pomodoro(work_time, short_break, long_break, cycle_len)

    # parse args

    # pomodoro with args
    pomodoro = Pomodoro(10, 10, 10, 10)

    # input_manager = InputManager()
    # input_manager.register(pomodoro.toggle_pause)

    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    loop.add_reader(sys.stdin, user_input, q, pomodoro)

    loop.run_until_complete(pomodoro.start())


if __name__ == '__main__':
    main()

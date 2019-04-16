import sys
import time
import asyncio


is_paused = False


class Pomodoro(object):
    def __init__(self, work_time, short_break, long_break, long_break_frequency):
        self.work_time = work_time
        self.short_break = short_break
        self.long_break = long_break
        self.long_break_frequency = long_break_frequency
        self.is_paused = False

    async def start(self):
        for i in range(self.long_break_frequency):
            await self.start_activity('work')
            if i != self.long_break_frequency - 1:
                await self.start_activity('break')
            else:
                await self.start_activity('long_break')

    async def start_activity(self, activity):
        if activity == 'work':
            print('work!')
            activity_time_min = self.work_time
        elif activity == 'break':
            print('break!')
            activity_time_min = self.short_break
        else:
            print('long break!')
            activity_time_min = self.long_break

        await self.start_counter(activity_time_min)

    async def start_counter(self, activity_time_min):
        activity_time_sec = activity_time_min*60
        sec = 0
        while True:
            await asyncio.sleep(1)
            if is_paused:
                continue
            else:
                if sec <  activity_time_sec:
                    seconds = sec % 60
                    minutes = (sec // 60) % 60
                    hours = (sec)//3600
                    print(f'{hours}:{minutes}:{seconds}', end='\r')
                    sec += 1


def user_input(q):
    asyncio.ensure_future(q.put(sys.stdin.readline()))
    global is_paused
    is_paused = not is_paused
    if is_paused:
        print('Paused')
    else:
        print('Continue')


def main():
    work_time = int(input('Set the work time in minutes: ').strip())
    short_break = int(input('Set the short rest time in minutes: ').strip())
    long_break = int(input('Set the long break time in minutes: ').strip())
    long_break_frequency = int(input('Set the long break frequency in minutes: ').strip())
    pomodoro = Pomodoro(work_time, short_break, long_break, long_break_frequency)

    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.add_reader(sys.stdin, user_input, q)
    loop.run_until_complete(pomodoro.start())


if __name__ == '__main__':
    main()

import time
import asyncio

class Pomodoro(object):
    def __init__(self, work_time, short_break, long_break, long_break_frequency):
        self.work_time = work_time
        self.short_break = short_break
        self.long_break = long_break
        self.long_break_frequency = long_break_frequency

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
        for sec in range(activity_time_sec):
            seconds = sec % 60
            minutes = (sec // 60) % 60
            hours = (sec)//3600
            print(f'{hours}:{minutes}:{seconds}', end='\r')
            await asyncio.sleep(1)


def main():
    work_time = int(input('Set the work time in minutes: ').strip())
    short_break = int(input('Set the short rest time in minutes: ').strip())
    long_break = int(input('Set the long break time in minutes: ').strip())
    long_break_frequency = int(input('Set the long break frequency in minutes: ').strip())
    loop = asyncio.get_event_loop()
    pomodoro = Pomodoro(work_time, short_break, long_break, long_break_frequency)
    loop.run_until_complete(pomodoro.start())



if __name__ == '__main__':
    main()

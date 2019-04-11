import time


class Pomodoro(object):
    def __init__(self, work_time, rest_time):
        self.work_time = work_time
        self.rest_time = rest_time

    def start(self):
        self.start_activity('work')
        self.start_activity('rest')

    def start_activity(self, activity):
        if activity == 'work':
            print('Work time!')
            activity_time_min = self.work_time
        else:
            print('Rest time!')
            activity_time_min = self.rest_time

        self.start_counter(activity_time_min)

    def start_counter(self, activity_time_min):
        activity_time_sec = activity_time_min*60
        for sec in range(activity_time_sec):
            seconds = sec % 60
            minutes = (sec // 60) % 60
            hours = (sec)//3600
            print(f'{hours}:{minutes}:{seconds}', end='\r')
            time.sleep(1/50)


def main():
    work_time = int(input('Set the work time in minutes: ').strip())
    rest_time = int(input('Set the rest time in minutes: ').strip())
    pomodoro = Pomodoro(work_time, rest_time)
    pomodoro.start()


if __name__ == '__main__':
    main()

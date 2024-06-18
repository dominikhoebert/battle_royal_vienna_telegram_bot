from threading import Timer
from time import time


class BotTimer:
    def __init__(self, name: str, interval: int, user_id: int, function, message: str = None, map: bool = False,
                 config: int = None):
        self.name = name
        self.interval = interval
        self.user_id = user_id
        self.function = function
        self.timer = Timer(interval * 60, self.function, [self])
        self.timer.start()
        self.running = True
        self.message = message
        self.map = map
        self.config = config
        self.start_time = time()

    def get_remaining_time(self):
        return self.interval - ((time() - self.start_time) / 60)

    def pause(self):
        if self.running:
            self.timer.cancel()
            self.interval = self.get_remaining_time()
            self.running = False

    def resume(self):
        if not self.running:
            self.timer = Timer(self.interval * 60, self.function, [self])
            self.timer.start()
            self.start_time = time()
            self.running = True

    def __eq__(self, other: str):
        return self.name == other


if __name__ == "__main__":
    t1 = BotTimer("test", 1, 1)
    t2 = BotTimer("test2", 2, 1)
    # t3 = BotTimer("test3", 3, 1)
    # print(t1.get_remaining_time())
    # print(t2.get_remaining_time())
    # print(t3.get_remaining_time())
    t1.pause()
    t1.resume()

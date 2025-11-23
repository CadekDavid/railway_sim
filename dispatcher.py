import threading
import time
from typing import List
from models.track import TrackSection


class Dispatcher(threading.Thread):

    def __init__(self, sections: List[TrackSection], logger, tick_s: float = 1.0):
        super().__init__(name="Dispatcher")
        self.sections = sections
        self.logger = logger
        self.tick_s = tick_s
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        self.logger.log("Dispatcher started")
        while not self._stop_event.is_set():
            occupied = []
            for s in self.sections:
                if s.occupied_by is not None:
                    occupied.append(f"{s.name}:{s.occupied_by}")
            if occupied:
                self.logger.log("Monitoring: occupied sections -> " + ", ".join(occupied))
            time.sleep(self.tick_s)

        self.logger.log("Dispatcher ended")

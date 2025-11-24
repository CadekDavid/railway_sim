from __future__ import annotations
import threading
import time
from typing import List
from .track import RouteStep, TrackSection


class Train(threading.Thread):

    def __init__(
        self,
        name: str,
        route: List[RouteStep],
        logger,
        start_delay_s: float = 0.0,
        speed_multiplier: float = 1.0
    ):
        super().__init__(name=name)
        self.route = route
        self.logger = logger
        self.start_delay_s = start_delay_s
        self.speed_multiplier = speed_multiplier
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        try:
            if self.start_delay_s > 0:
                time.sleep(self.start_delay_s)

            self.logger.log(f"{self.name} starting route")

            for i, step in enumerate(self.route):
                if self._stop_event.is_set():
                    self.logger.log(f"{self.name} stopped")
                    break

                # station arrival
                try:
                    step.station.arrive(self.name, self.logger)
                except Exception as e:
                    self.logger.log(f"ERROR in station.arrive for {self.name}: {e}")
                    continue

                time.sleep(step.dwell_time_s / self.speed_multiplier)

                # station depart
                try:
                    step.station.depart(self.name, self.logger)
                except Exception as e:
                    self.logger.log(f"ERROR in station.depart for {self.name}: {e}")

                if step.outgoing_section is None:
                    self.logger.log(f"{self.name} finished at {step.station.name}")
                    break

                self._travel_section(step.outgoing_section)

        except Exception as e:
            self.logger.log(f"CRITICAL ERROR in Train.run of {self.name}: {e}")

        finally:
            self.logger.log(f"{self.name} route thread ends")

    def _travel_section(self, section: TrackSection):

        ok = section.acquire(self.name, self.logger)
        if not ok:
            self.logger.log(f"{self.name} could not acquire {section.name}")
            return


        time.sleep(section.travel_time_s / self.speed_multiplier)


        section.release(self.name, self.logger)

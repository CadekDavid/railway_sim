from __future__ import annotations
import threading
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TrackSection:

    section_id: int
    name: str
    travel_time_s: float

    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _cond: threading.Condition = field(init=False)
    occupied_by: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        self._cond = threading.Condition(self._lock)

    def acquire(self, train_name: str, logger, timeout: Optional[float] = None) -> bool:

        with self._lock:
            if timeout is None:
                while self.occupied_by is not None:
                    logger.log(f"{train_name} waits for section {self.name} (occupied by {self.occupied_by})")
                    self._cond.wait()
                self.occupied_by = train_name
                logger.log(f"{train_name} ENTERS section {self.name}")
                return True
            else:

                end = threading.current_thread()

                import time
                deadline = time.time() + timeout
                while self.occupied_by is not None:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        return False
                    logger.log(f"{train_name} waits for section {self.name} (occupied by {self.occupied_by})")
                    self._cond.wait(timeout=remaining)

                self.occupied_by = train_name
                logger.log(f"{train_name} ENTERS section {self.name}")
                return True

    def release(self, train_name: str, logger):
        with self._lock:
            if self.occupied_by != train_name:

                logger.log(f"WARNING: {train_name} tried to leave {self.name}, but occupied_by={self.occupied_by}")
                return
            self.occupied_by = None
            logger.log(f"{train_name} LEAVES section {self.name}")
            self._cond.notify_all()


@dataclass
class Station:

    name: str
    platforms: int

    _sem: threading.Semaphore = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    occupied_platforms: int = field(default=0, init=False)

    def __post_init__(self):
        self._sem = threading.Semaphore(self.platforms)

    def arrive(self, train_name: str, logger):
        self._sem.acquire()
        with self._lock:
            self.occupied_platforms += 1
            logger.log(f"{train_name} ARRIVES at station {self.name} "
                       f"(platforms used {self.occupied_platforms}/{self.platforms})")

    def depart(self, train_name: str, logger):
        with self._lock:
            self.occupied_platforms -= 1
            logger.log(f"{train_name} DEPARTS station {self.name} "
                       f"(platforms used {self.occupied_platforms}/{self.platforms})")
        self._sem.release()


@dataclass
class RouteStep:

    station: Station
    outgoing_section: Optional[TrackSection] = None
    dwell_time_s: float = 1.0

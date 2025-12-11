from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
from models.track import Station, TrackSection, RouteStep


@dataclass
class TrainRequest:

    name: str
    route: List[RouteStep]
    desired_start_s: float


@dataclass
class ScheduledTrain:

    name: str
    route: List[RouteStep]
    scheduled_start_s: float
    delay_s: float


@dataclass
class Occupancy:

    station_intervals: Dict[Station, List[Tuple[float, float]]]
    section_intervals: Dict[TrackSection, List[Tuple[float, float]]]


def compute_occupancy(route: List[RouteStep], start_s: float) -> Occupancy:

    station_occ: Dict[Station, List[Tuple[float, float]]] = {}
    section_occ: Dict[TrackSection, List[Tuple[float, float]]] = {}

    t = start_s
    for step in route:
        arr = t
        dep = t + step.dwell_time_s
        station_occ.setdefault(step.station, []).append((arr, dep))
        t = dep


        if step.outgoing_section is None:
            break


        enter = t
        leave = t + step.outgoing_section.travel_time_s
        section_occ.setdefault(step.outgoing_section, []).append((enter, leave))
        t = leave

    return Occupancy(station_occ, section_occ)


def intervals_overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> bool:

    return (a_start < b_end) and (b_start < a_end)


def has_conflict(
    occ: Occupancy,
    existing_station: Dict[Station, List[Tuple[float, float]]],
    existing_section: Dict[TrackSection, List[Tuple[float, float]]],
) -> bool:



    for section, new_intervals in occ.section_intervals.items():
        existing = existing_section.get(section, [])
        for (ns, ne) in new_intervals:
            for (es, ee) in existing:
                if intervals_overlap(ns, ne, es, ee):
                    return True


    for station, new_intervals in occ.station_intervals.items():
        existing = existing_station.get(station, [])
        for (ns, ne) in new_intervals:

            concurrent = 0
            for (es, ee) in existing:
                if intervals_overlap(ns, ne, es, ee):
                    concurrent += 1

            if concurrent >= station.platforms:
                return True

    return False


def plan_timetable(
    requests: List[TrainRequest],
    logger,
    max_delay_s: float = 3600.0,
    step_s: float = 60.0,
) -> List[ScheduledTrain]:


    scheduled: List[ScheduledTrain] = []
    station_occ: Dict[Station, List[Tuple[float, float]]] = {}
    section_occ: Dict[TrackSection, List[Tuple[float, float]]] = {}


    for req in sorted(requests, key=lambda r: r.desired_start_s):
        start = req.desired_start_s
        chosen_start = None

        while start <= req.desired_start_s + max_delay_s:
            occ = compute_occupancy(req.route, start)
            if not has_conflict(occ, station_occ, section_occ):
                chosen_start = start
                break
            start += step_s

        if chosen_start is None:
            logger.log(f"WARNING: požadavek vlaku {req.name} se nepodařilo "
                       f"naplánovat ani při zpoždění {max_delay_s}s – přeskakuji.")
            continue

        delay = chosen_start - req.desired_start_s
        logger.log(
            f"Plán: vlak {req.name} vyjede v t={chosen_start:.1f}s "
            f"(zpoždění oproti požadavku {delay:.1f}s)"
        )

        occ = compute_occupancy(req.route, chosen_start)
        for st, intervals in occ.station_intervals.items():
            station_occ.setdefault(st, []).extend(intervals)
        for sec, intervals in occ.section_intervals.items():
            section_occ.setdefault(sec, []).extend(intervals)

        scheduled.append(
            ScheduledTrain(
                name=req.name,
                route=req.route,
                scheduled_start_s=chosen_start,
                delay_s=delay,
            )
        )

    return scheduled

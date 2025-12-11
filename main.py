from utils.logger import Logger
from models.track import Station, TrackSection, RouteStep
from models.train import Train
from dispatcher import Dispatcher
from planner import TrainRequest, plan_timetable


def build_demo_world(logger: Logger):

    A = Station("A", platforms=1)
    B = Station("B", platforms=1)
    C = Station("C", platforms=1)
    D = Station("D", platforms=1)


    AB = TrackSection(1, "AB", travel_time_s=2.5)
    BC = TrackSection(2, "BC", travel_time_s=2.0)
    BD = TrackSection(3, "BD", travel_time_s=3.0)


    route_T1 = [
        RouteStep(A, outgoing_section=AB, dwell_time_s=1.0),
        RouteStep(B, outgoing_section=BC, dwell_time_s=1.2),
        RouteStep(C, outgoing_section=None, dwell_time_s=0.5)
    ]

    route_T2 = [
        RouteStep(C, outgoing_section=BC, dwell_time_s=0.8),
        RouteStep(B, outgoing_section=AB, dwell_time_s=1.0),
        RouteStep(A, outgoing_section=None, dwell_time_s=0.5)
    ]

    route_T3 = [
        RouteStep(D, outgoing_section=BD, dwell_time_s=0.7),
        RouteStep(B, outgoing_section=BC, dwell_time_s=1.1),
        RouteStep(C, outgoing_section=None, dwell_time_s=0.5)
    ]

    sections = [AB, BC, BD]
    stations = [A, B, C, D]
    routes = {"T1": route_T1, "T2": route_T2, "T3": route_T3}

    return stations, sections, routes


def main():
    logger = Logger()
    stations, sections, routes = build_demo_world(logger)


    requests = [
        TrainRequest("T1", routes["T1"], desired_start_s=0.0),
        TrainRequest("T2", routes["T2"], desired_start_s=0.0),
        TrainRequest("T3", routes["T3"], desired_start_s=120.0),
    ]


    scheduled = plan_timetable(requests, logger, max_delay_s=1800.0, step_s=60.0)


    trains: list[Train] = []
    for st in scheduled:
        train = Train(
            name=st.name,
            route=st.route,
            logger=logger,
            start_delay_s=st.scheduled_start_s,
            speed_multiplier=1.0,
        )
        trains.append(train)


    disp = Dispatcher(sections, logger, tick_s=1.0)


    disp.start()
    for t in trains:
        t.start()


    for t in trains:
        t.join()


    disp.stop()
    disp.join()

    logger.log("Simulation finished")

if __name__ == "__main__":
    main()

from utils.logger import Logger
from models.track import Station, TrackSection, RouteStep
from models.train import Train
from dispatcher import Dispatcher


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

    t1 = Train("T1", routes["T1"], logger, start_delay_s=0.0, speed_multiplier=1.0)
    t2 = Train("T2", routes["T2"], logger, start_delay_s=0.5, speed_multiplier=1.0)
    t3 = Train("T3", routes["T3"], logger, start_delay_s=1.0, speed_multiplier=1.0)

    disp = Dispatcher(sections, logger, tick_s=1.0)

    disp.start()
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    disp.stop()
    disp.join()

    logger.log("Simulation finished")


if __name__ == "__main__":
    main()

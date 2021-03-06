#!python

from collections import defaultdict
from datetime import datetime


# #-- CALCULATION OF TIME DELTA --##
# tag::header[]
# tag::get_delay[]
def get_delay(expected: str, takeoff: str) -> int:
    """\
    Measure the time difference in minutes between two times
    delay = <take-off> - <expected>

    Args:
        expected: expected departure time (e.g. 23:45)
        takeoff: real departure time (e.g. 23:55)
    """
    # end::header[]
    time_fmt = "%H:%M"
    # We convert with strptime and calculate the difference
    t_real = datetime.strptime(takeoff, time_fmt)
    t_exp = datetime.strptime(expected, time_fmt)
    delta = t_real - t_exp

    # If "takeoff < expected", we will call recursively and multiply by "-1"
    if delta.days < 0:
        return -1 * get_delay(takeoff, expected)

    # If delta is bigger than half-day, we will return (delta - 1 day)
    sec_in_day = 60 * 60 * 24
    if delta.seconds > sec_in_day / 2:
        seconds = delta.seconds - sec_in_day
    else:
        seconds = delta.seconds
    return int(seconds / 60)


def get_delay_2(expected: str, takeoff: str) -> int:
    """\
    Measure the time difference in minutes between two times
    delay = <take-off> - <expected>

    Args:
        expected: expected departure time (e.g. 23:45)
        takeoff: real departure time (e.g. 23:55)
    """

    def min_in_time(hhmm: str):
        t = hhmm.split(":")
        return int(t[0]) * 60 + int(t[1])

    # We convert by doing HH * 60 + MM and calculate the difference
    # If "takeoff < expected", the result is we will have to deduct 1 day from delta
    # However, we will calculate normally if delta is bigger than half-day
    min_in_day = 60 * 24
    delta = min_in_time(takeoff) - min_in_time(expected)
    if delta < 0:
        return -1 * get_delay_2(takeoff, expected)
    elif delta > min_in_day / 2:
        return delta - min_in_day
    else:
        return delta
# end::get_delay[]


# tag::header[]


class Airline:
    """Class describing an airline with records"""

    def __init__(self, name, code):
        """Creation of an airline with records"""
        self.name = name
        self.code = code
        self.flights = defaultdict(list)  # So ".append(...)" will work automatically
        self.destination = dict()

    # tag::add_info[]
    def add_info(self, record):
        """Add flight information, create flight if it does not exist

        Args:
            record(dict): dictionary with keys:
                * 'date': date of the flight, stored as a string (e.g. "2018-02-30")
                * 'time': expected take-off time, stored as a string (e.g. "15:30")
                * 'code': code of flight (e.g. "MU123")
                * 'destination'
                * 'take-off': real take-off time, stored as a string
        """
        # end::header[]
        code = record["code"]

        # Save destination
        if code not in self.destination:
            self.destination[code] = record["destination"]
            # self.flights[code] = list()  # mandatory if defaultdict(list) is not used

        # Record to save in the list of records
        # saved_record = {k: record[k] for k in ("date", "time")}
        saved_record = {
            "date": record["date"],
            "time": record["time"],
            "delay": get_delay(record["time"], record["take-off"]),
        }

        # Save record (NOTE: defaultdict ensure to initialize the list)
        self.flights[code].append(saved_record)

    # end::add_info[]
    # tag::header[]

    # tag::get_rating_flight[]
    def get_rating_flight(self, flight: str):
        """Get the rating of a given flight

        Args:
            flight: code of a flight

        Returns:
            ('% late', 'average delay') for a flight, both int
        """
        # end::header[]
        # Flight unknown
        if flight not in self.flights:
            return None, None
        # Known flight: calculate number of flights late and total delay
        nb_late, total_delay = 0.0, 0.0
        for record in self.flights[flight]:
            total_delay += record["delay"]
            if record["delay"] > 30:
                nb_late += 1

        nb_flights = len(self.flights[flight])
        percent = int(nb_late / nb_flights * 100)
        average = int(total_delay / nb_flights)
        return percent, average

    # end::get_rating_flight[]
    # tag::header[]

    # tag::get_rating_airline[]
    def get_rating_airline(self):
        """Get the rating of the airline

        Returns:
            ('% late', 'average delay') for the airline, both int
        """
        # end::header[]
        # We could use the previous version to avoid duplicate code
        # HOWEVER, get_rating_flight returns "int" so the result would be inexact
        # We will do a copy of the code with a loop on "flight" [arghhh :( duplicate code!!]
        nb_late, total_delay = 0.0, 0.0
        nb_flights = 0
        for records in self.flights.values():
            nb_flights += len(records)
            for record in records:
                total_delay += record["delay"]
                if record["delay"] > 30:
                    nb_late += 1

        percent = int(nb_late / nb_flights * 100)
        average = int(total_delay / nb_flights)
        return percent, average
    # end::get_rating_airline[]


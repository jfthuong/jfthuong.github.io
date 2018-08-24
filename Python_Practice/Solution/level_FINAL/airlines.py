#!python

from collections import defaultdict
from datetime import datetime


# #-- CALCULATION OF TIME DELTA --##
def get_delay(expected:str, takeoff:str) -> int:
    """\
    Measure the time difference in minutes between two times
    delay = <take-off> - <expected>

    Args:
        expected: expected departure time (e.g. 23:45)
        takeoff: real departure time (e.g. 23:55)
    """
    time_fmt = "%H:%M"
    # We convert with strptime and calculate the difference
    # If "takeoff < expected", the result is {day = -1, sec = delta + 1 day} 
    # ... so we will have to deduct 1 day from the delta
    # However, we will calculate normally if delta is bigger than half-day
    t_real = datetime.strptime(takeoff, time_fmt)
    t_exp = datetime.strptime(expected, time_fmt)
    delta = t_real - t_exp
    # Calculate delay (can be negative - first case)
    sec_in_day = 60 * 60 * 24
    if delta.days < 0 and delta.seconds > sec_in_day/2:
        seconds = delta.seconds - sec_in_day
    else:
        seconds = delta.seconds
    return int(seconds / 60)




class Airline():
    """Class describing an airline with records"""

    def __init__(self, name, code):
        """Creation of an airline with records"""
        self.name = name
        self.code = code
        self.flights = defaultdict(list)
        self.destination = dict()

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
        pass

    def get_rating_flight(self, flight:str):
        """Get the rating of a given flight

        Args:
            flight: code of a flight

        Returns:
            ('% late', 'average delay') for a flight, both int
        """
        pass

    def get_rating_airline(self):
        """Get the rating of the airline

        Returns:
            ('% late', 'average delay') for the airline, both int
        """
        pass


if __name__ == "__main__":

    import doctest
    doctest.testmod()


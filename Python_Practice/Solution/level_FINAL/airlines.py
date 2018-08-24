#!python

# #-- CALCULATION OF TIME DELTA --##
from datetime import datetime


def get_delay(time, takeOff):
    """Measure the time difference between two times
    >>> get_delay('12:10','12:45')
    35
    >>> get_delay('12:10','11:45')
    -25
    """
    format = "%H:%M"
    delta = datetime.strptime(takeOff, format) - datetime.strptime(time, format)
    # Calculate delay (can be negative - first case)
    if delta.days < 0:
        delay = (delta.seconds - 60 * 60 * 24) / 60
    else:
        delay = delta.seconds / 60
    return int(delay)


# #-------------------------------##



class Airline():
    """Class describing an airline with records"""

    def __init__(self, name, code):
        """Creation of an airline with records"""
        self.name = name
        self.code = code
        self.flights = dict()
        self.destination = dict()

    def add_info(self, record):
        """Add record to the list of flights
            (dict) -> None
            record = dictionary with keys: 'date', 'time', 'code', 'airline', 'destination', 'take-off'
        """
        code = record["code"]

        # Save destination
        if code not in self.destination:
            self.destination[code] = record["destination"]

            # Record to save in the list of records
        saved_record = {k: record[k] for k in ("date", "time")}
        saved_record["delay"] = get_delay(record["time"], record["take-off"])

        # Save record
        if code in self.flights:
            self.flights[code].append(saved_record)
        else:
            self.flights[code] = [saved_record]

    def get_rating_flight(self, flight):
        """Get the rating of a given flight
           (string) -> ('% late':int, 'avg delay':int)
        """
        # Flight unknown
        if flight not in self.flights:
            return None, None
            # Known flight: calculate number of flights late and total delay
        nb_late, total_delay = 0.0, 0.0
        for record in self.flights[flight]:
            total_delay += record["delay"]
            if record["delay"] > 30:
                nb_late += 1
                # Return result
        percent = int(nb_late / len(self.flights[flight]) * 100)
        average = int(total_delay / len(self.flights[flight]))
        return percent, average

    def get_rating_airline(self):
        """Get the rating of the airline
        (None) -> ('% late':int, 'avg delay':int)

        >>> ChinaEastern=Airline('China Eastern',  'MU')
        >>> ChinaEastern.add_info({'date':'2015-08-24', 'time':'12:00', 'code':'MU155', 'destination':'CDG', 'take-off':'13:46'})
        >>> ChinaEastern.get_rating_airline()
        (100, 106)
        >>> AirFrance=Airline('Air France',  'AF')
        >>> AirFrance.add_info({'date':'2015-08-24', 'time':'12:00', 'code':'AF117', 'destination':'CDG', 'take-off':'13:46'})
        >>> AirFrance.add_info({'date':'2015-08-25', 'time':'12:00', 'code':'AF117', 'destination':'CDG', 'take-off':'12:16'})
        >>> AirFrance.add_info({'date':'2015-08-24', 'time':'12:00', 'code':'AF120', 'destination':'JFK', 'take-off':'11:46'})
        >>> AirFrance.add_info({'date':'2015-08-25', 'time':'12:00', 'code':'AF120', 'destination':'JFK', 'take-off':'15:46'})
        >>> AirFrance.get_rating_airline()
        (50, 83)
        """
        nb_late, total_delay, total_flights = 0.0, 0.0, 0
        # Get rating of airline based on ratings from flights
        for flight, records in self.flights.items():
            total_flights += len(records)
            # Get ratings of each flight
            percent, average = self.get_rating_flight(flight)
            nb_late += percent / 100. * len(records)
            total_delay += average * len(records)
            # Return result
        percent = int(nb_late / total_flights * 100)
        average = int(total_delay / total_flights)
        return percent, average


if __name__ == "__main__":

    import doctest
    doctest.testmod()


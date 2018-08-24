#!python

##############
# HOW TO RUN #
##############
# 1. Install Pytest
"pip install pytest"
# 2. Run Tests
"pytest -v test_airlines.py"
# NOTE: if "pytest" is not found, run "python -m pytest ..."
##############

import pytest
from typing import Dict, List, Any

from airlines import Airline, get_delay
import processRecords as rec


def test_delay():
    assert get_delay("12:10", "12:45") == 35
    assert get_delay("12:10", "11:45") == -25
    assert get_delay("23:45", "00:45") == 60


# Test class "Airline"
class Test_Airline:
    """Test class 'Airline'"""

    def test_01_init(self):
        """	Test initialization of class Airline"""
        sq = Airline("Singapore Airlines", "SQ")
        assert sq.flights == {}
        assert sq.destination == {}
        assert sq.name == "Singapore Airlines"
        assert sq.code == "SQ"

    def add_info_SQ_MU(self):
        """Function to add records - to be used for other tests"""
        sq = Airline("Singapore Airlines", "SQ")
        mu = Airline("China Eastern", "MU")
        sq.add_info(
            {
                "date": "2015-08-20",
                "time": "08:05",
                "code": "SQ827",
                "destination": "Singapore",
                "take-off": "09:08",
            }
        )

        sq.add_info(
            {
                "date": "2015-08-21",
                "time": "08:05",
                "code": "SQ827",
                "destination": "Singapore",
                "take-off": "08:35",
            }
        )

        mu.add_info(
            {
                "date": "2015-08-20",
                "time": "08:20",
                "code": "MU511",
                "destination": "Osaka Kansai",
                "take-off": "8:25",
            }
        )
        mu.add_info(
            {
                "date": "2015-08-20",
                "time": "08:30",
                "code": "MU721",
                "destination": "Seoul",
                "take-off": "9:30",
            }
        )
        return sq, mu

    def test_02_add_info(self):
        """Add record to list of flights"""
        sq, mu = self.add_info_SQ_MU()

        assert sq.flights == {
            "SQ827": [
                {"date": "2015-08-20", "delay": 63, "time": "08:05"},
                {"date": "2015-08-21", "delay": 30, "time": "08:05"},
            ]
        }
        assert sq.destination == {"SQ827": "Singapore"}

        assert mu.flights == {
            "MU511": [{"date": "2015-08-20", "delay": 5, "time": "08:20"}],
            "MU721": [{"date": "2015-08-20", "delay": 60, "time": "08:30"}],
        }
        assert mu.destination == {"MU511": "Osaka Kansai", "MU721": "Seoul"}

    def test_03_get_rating_flight(self):
        """Get the rating of a given flight"""
        sq, mu = self.add_info_SQ_MU()
        assert sq.get_rating_flight("SQ827") == (50, 46)
        assert mu.get_rating_flight("MU511") == (0, 5)

    def test_04_get_rating_airline(self):
        """Get the rating of the airline"""
        sq, mu = self.add_info_SQ_MU()
        assert sq.get_rating_airline() == (50, 46)
        assert mu.get_rating_airline() == (50, 32)


# Test main program
class TestMain(object):
    """Test main program (processRecords.py)"""

    def test_01_read_flight_records_robustness(self):
        """Read flight records from an unknown file"""
        with pytest.raises(IOError):
            rec.read_flight_records("unknown.txt")

    def test_01_read_flight_records(self):
        """Read flight records from an existing file"""

        records = rec.read_flight_records("mini_record.txt")
        assert records == [
            {
                "code": "EK303",
                "take-off": "0:41",
                "destination": "Dubai",
                "airline": "Emirates Airlines",
                "time": "0:05",
                "date": "2015-08-20",
            },
            {
                "code": "MU553",
                "take-off": "0:15",
                "destination": "Paris Ch. de Gaulle",
                "airline": "China Eastern Airlines",
                "time": "0:05",
                "date": "2015-08-20",
            },
            {
                "code": "MU219",
                "take-off": "0:45",
                "destination": "Frankfurt",
                "airline": "China Eastern Airlines",
                "time": "0:05",
                "date": "2015-08-20",
            },
        ]

    def test_02_get_ratings_flight(self):
        """Get rating of flight"""
        af = Airline("Air France", "Air France")
        af.add_info(
            {
                "date": "2015-08-24",
                "time": "12:00",
                "code": "AF117",
                "destination": "CDG",
                "take-off": "12:46",
            }
        )

        assert af.get_rating_flight("Unknown") == (None, None)
        assert af.get_rating_flight("AF117") == (100, 46)

        af.add_info(
            {
                "date": "2015-08-24",
                "time": "12:00",
                "code": "AF117",
                "destination": "CDG",
                "take-off": "11:46",
            }
        )
        assert af.get_rating_flight("AF117") == (50, 16)

    def test_03_get_ratings_airline(self):
        """Get ratings of airlines based on the records"""
        records = rec.read_flight_records("mini_record.txt")
        airlines = rec.get_ratings_airlines(records)
        assert airlines["Emirates Airlines"].__dict__ == {
            "destination": {"EK303": "Dubai"},
            "flights": {"EK303": [{"date": "2015-08-20", "delay": 36, "time": "0:05"}]},
            "code": "EK",
            "name": "Emirates Airlines",
        }
        assert airlines["China Eastern Airlines"].__dict__ == {
            "destination": {"MU553": "Paris Ch. de Gaulle", "MU219": "Frankfurt"},
            "flights": {
                "MU553": [{"date": "2015-08-20", "delay": 10, "time": "0:05"}],
                "MU219": [{"date": "2015-08-20", "delay": 40, "time": "0:05"}],
            },
            "code": "MU",
            "name": "China Eastern Airlines",
        }

    def test_04_list_sorted_ratings(self):
        """Sort the airlines and flights based on the chances to be late"""
        records = rec.read_flight_records("mini_record.txt")
        airlines = rec.get_ratings_airlines(records)
        rating_airlines, rating_flights = rec.list_sorted_ratings(airlines)
        assert rating_airlines == [
            ("China Eastern Airlines", 50, 25),
            ("Emirates Airlines", 100, 36),
        ]
        assert rating_flights == [
            ("MU553", 0, 10),
            ("EK303", 100, 36),
            ("MU219", 100, 40),
        ]

    def test_04_get_first_last_elem(self):
        """Return lists with first/last <nb_elem> elements"""
        first, last = rec.get_first_last_elem(["f", "e", "d", "c", "b", "a"], 0)
        assert first == []
        assert last == []

        first, last = rec.get_first_last_elem(["f", "e", "d", "c", "b", "a"], 4)
        assert first == ["f", "e", "d", "c"]
        assert last == ["a", "b", "c", "d"]

        rating_flights = [("AA", 100), ("ZZ", 2), ("CC", 3), ("dd", 400), ("EE", 3)]
        first, last = rec.get_first_last_elem(rating_flights, 2)
        assert first == [("AA", 100), ("ZZ", 2)]
        assert last == [("EE", 3), ("dd", 400)]


if __name__ == "__main__":
    pytest.main(args=["-v"])


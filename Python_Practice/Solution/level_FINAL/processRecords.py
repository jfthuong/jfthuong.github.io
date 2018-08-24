#!python

import airlines
import re, argparse, datetime


def read_flight_records(file_path):
    """Read flight records from a given file
    (file_path:string) -> (list_records:list)
    Output: list of take off records, each element is a dict with keys: date, time, code, airline, destination, take-off
    """
    list_records = list()

    try:
        with open(file_path) as f:
            for record in f:
                format = r"^([\d\-]+),\s*([\d:]+),\s*([A-Z0-9]+),\s*([\w ]+),\s*(\w.+?),\s*([\d:]+)"
                match_record = re.match(format, record)
                if match_record:
                    record_keys = [
                        "date",
                        "time",
                        "code",
                        "airline",
                        "destination",
                        "take-off",
                    ]
                    record_dict = dict()
                    for i in range(len(match_record.groups())):
                        record_dict[record_keys[i]] = match_record.group(i + 1)
                    list_records.append(record_dict)
    except Exception as e:
        raise IOError("Error while trying to open input file 'file_path': %s" % e)

    return list_records


def get_ratings_airlines(list_records):
    """Get ratings of airlines based on the records
    (list_records:list) -> (airlines_list:dict)
    Output: dictionary with key=airline name, value=Object of class "Airline_record" with all the records of that airline
    """
    airlines_list = dict()

    for record in list_records:
        name = record["airline"]
        # Create airline if required
        if name not in airlines_list:
            code = record["code"][:2]
            airlines_list[name] = airlines.Airline(name, code)
        # Add the record information
        airlines_list[name].add_info(record)

    return airlines_list


def list_sorted_ratings(airlines_list, n_elem=None):
    """Sort the airlines and flights based on the chances to be late
    (airlines_list:dict, [n_elem:int]) -> ( rating_airlines:list, rating_flights:list )
    Each element of the list contain the following tuples: (<airline|flight code>, <% late>, <average delay>)
    """
    rating_airlines, rating_flights = [], []

    # Generate the lists
    for name, airline in airlines_list.items():
        # Airline
        rating_airline = airline.get_rating_airline()
        rating_airlines.append((name, rating_airline[0], rating_airline[1]))
        # Flights
        for flight in airline.flights.keys():
            rating_flight = airline.get_rating_flight(flight)
            rating_flights.append((flight, rating_flight[0], rating_flight[1]))

    # Sort the lists
    rating_airlines = sorted(rating_airlines, key=lambda x: x[1] * 1000 + x[2])
    rating_flights = sorted(rating_flights, key=lambda x: x[1] * 1000 + x[2])

    return rating_airlines, rating_flights


def get_first_last_elem(sorted_list, nb_elem):
    """Return lists with first/last <nb_elem> elements
    (list, int) -> (list, list)
    """
    if nb_elem < 1:
        return [], []
    else:
        first_elements = sorted_list[:nb_elem]
        last_elements = sorted_list[-1 * nb_elem :]
        last_elements.reverse()
        return first_elements, last_elements


##=== MAIN PROGRAM ===##
if __name__ == "__main__":
    # Unit test
    import doctest

    doctest.testmod()

    # Main Program
    description = """processRecords.py - Generating a report of airines and flights based on their delay"""

    # Parsing options and arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_path")
    parser.add_argument(
        "-o",
        "--output",
        dest="report_path",
        default="report_airlines.html",
        action="store",
    )
    parser.add_argument("-n", dest="nb_ranking", action="store", default=10, type=int)
    cmd = parser.parse_args()
    # =DEBUG=#
    # cmd = parser.parse_args(["list_records.txt"])

    # Getting list of sorted elements
    records = read_flight_records(cmd.input_path)
    airlines_list = get_ratings_airlines(records)
    rating_airlines, rating_flights = list_sorted_ratings(airlines_list)

    # Generate list of  best and worse <nb_ranking> airlines/flights
    rating_best_airlines, rating_worse_airlines = get_first_last_elem(
        rating_airlines, cmd.nb_ranking
    )
    rating_best_flights, rating_worse_flights = get_first_last_elem(
        rating_flights, cmd.nb_ranking
    )

    # Retrieve template of report
    try:
        with open("report_Template.html") as f:
            template = f.read()
            template = template.replace("{background", "{{background").replace(
                ";}", ";}}"
            )
    except Exception as e:
        msg = f"Error while trying to read template 'report_Template.html' ({e})"
        print(msg)
        template = f"<html><body>{msg}</body></html>"

    # Prepare the report
    report = {}
    # time
    report["date"] = str(datetime.date.today())
    report["time"] = str(datetime.datetime.now().time())[:8]
    # rankings
    def store_ranking(key, ranking):
        report[key] = "</li>\n<li>".join(
            ["<b>%s</b> (%d%%, avg=%d min)" % tuple for tuple in ranking]
        )

    store_ranking("best_airlines", rating_best_airlines)
    store_ranking("worse_airlines", rating_worse_airlines)
    store_ranking("best_flights", rating_best_flights)
    store_ranking("worse_flights", rating_worse_flights)

    # Generate the report
    report_content = template.format(**report)
    try:
        with open(cmd.report_path, "w") as f:
            f.write(report_content)

    except Exception as e:
        print(f"Error while trying to write in '{cmd.report}' ({e})")

#!python

import airlines
import re, argparse, datetime


def read_flight_records(file_path: str):
    """\
    Read flight records from a given file and returns the list of take-off records.
    Each element is a dict with keys: date, time, code, airline, destination, take-off

    Args:
        file_path: Path of file to read

    Returns:
        list of take off records
    """
    list_records = list()
    record_keys = ["date", "time", "code", "airline", "destination", "take-off"]

    # We will extract each info and match it to "record_keys" by using zip(l1, l2)
    # NOTE: zip transforms 2 list in a list of tuple; for example:
    #       zip([1, 2, 3], ["a", "b", "c"]) => [(1, "a"), (2, "b"), (3, "c")]
    # Using "dict(...)" on this zipped list will create a dictionary with key and value

    # 2 solutions to split line in elements
    # Solution #1: Using regular expression to ensure strict pattern matchin
    pattern = (
        r"^([\d\-]+),\s*([\d:]+),\s*([A-Z0-9]+),\s*([\w ]+),\s*(\w.+?),\s*([\d:]+)"
    )
    # Solution #2: using <line>.split(",") and stripping all spaces around each element
    try:
        with open(file_path) as f:
            for record in f:
                # == Solution #1 (regex) ==
                # if record.strip() == "":
                #     continue  # Skip empty lines
                # match_record = re.match(pattern, record)
                # if match_record:
                #     record_dict = dict(zip(record_keys, match_record.groups()))
                #     list_records.append(record_dict)
                # else:
                #     print(f"Following line of {file_path!r} does not match pattern: {record!r}")

                # == Solution #2 (split) ==
                if record.strip() == "":
                    continue  # Skip empty lines
                data = [d.strip() for d in record.split(",")]
                # NOTE: we can also use regular expression
                # data = re.split(r"\s*,\s*", record.rstrip())
                if len(data) != len(record_keys):
                    print(
                        f"Following line of {file_path!r} has incorrect number of data: {record!r}"
                    )
                else:
                    record_dict = dict(zip(record_keys, data))
                    list_records.append(record_dict)

    except Exception as e:
        raise IOError(f"Error while trying to read input file {file_path!r}: {e}")

    return list_records


def get_ratings_airlines(list_records):
    """From the list of records, create a dictionary with all Airlines

    Args:
        list_records(list): list of dict returned by read_flight_records

    Returns:
        dictionary "airlines_dic" with:
        * key = airline name
        * value = "Airline" object with all the records of that airline
    """
    # We will loop each element of input list and
    # * Create a new Airline if it does not exist in the dictionary
    # * Add the record in the Airline object
    airlines_dic = dict()

    for record in list_records:
        name = record["airline"]
        # Create airline if required
        if name not in airlines_dic:
            code = record["code"][:2]  # First 2 characters of flight
            airlines_dic[name] = airlines.Airline(name, code)
        # Add the record information
        airlines_dic[name].add_info(record)

    return airlines_dic


def list_sorted_ratings(airlines_dic):
    """Sort the airlines and flights based on the probability to be late

    Args:
        airlines_dic(dict): Dictionary with Airline objects

    Returns:
        rating_airlines(list): list of Airlines sorted by late probability (less late first)
        rating_flights(list): list of flights sorted by late probability (less late first)

    NOTE: Each element of the returned lists contains the following tuple:
        (<airline|flight code>, <% late>, <average delay>)
    """
    rating_airlines = list()
    rating_flights = list()

    # Generate the lists
    for name, airline in airlines_dic.items():
        # Airline
        rating_airline = airline.get_rating_airline()
        # NOTE: We add the name before the tuple by using "*args" to get elements of tuple
        # name_code = f"{name} [{airline.code}]"
        # rating_airlines.append((name_code, *rating_airline))
        rating_airlines.append((name, *rating_airline))
        # Flights
        for flight in airline.flights.keys():
            rating_flight = airline.get_rating_flight(flight)
            # code_dest = f"{flight} ({airline.destination[flight]})"
            # rating_flights.append((code_dest, *rating_flight))
            rating_flights.append((flight, *rating_flight))

    # Sort the lists based on the probability to be late
    def score_airline(t):
        """From tuple (% late, average delay) calculates a score
        "% late" * 1000 + "average delay" to sort the airlines
        """
        return t[1] * 1000 + t[2]

    rating_airlines = sorted(rating_airlines, key=score_airline)
    rating_flights = sorted(rating_flights, key=score_airline)

    return rating_airlines, rating_flights


def get_first_last_elem(sorted_list, nb_elem: int):
    """Return lists with first/last <nb_elem> elements

    Args:
        sorted_list(list): list of elements
        nb_elem(int): number of first/last elements

    Return:
        first(list): first nb_elem elements of sorted_list
        last(list): last nb_elem elements of sorted_list in reverse order
    """
    if nb_elem < 1:
        return [], []
    else:
        first_elements = sorted_list[:nb_elem]
        last_elements = sorted_list[-nb_elem:]
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
        "-o", "--output", dest="report_path", default="report_airlines.html"
    )
    parser.add_argument("-n", dest="nb_ranking", default=10, type=int)
    cmd = parser.parse_args()
    # =DEBUG=#
    # cmd = parser.parse_args(["list_records.txt"])

    # Getting list of sorted elements
    records = read_flight_records(cmd.input_path)
    airlines_dic = get_ratings_airlines(records)
    rating_airlines, rating_flights = list_sorted_ratings(airlines_dic)

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
            template = template.replace("{background", "{{background")
            template = template.replace(";}", ";}}")
    except Exception as e:
        msg = f"Error while trying to read template 'report_Template.html' ({e})"
        print(msg)
        template = f"<html><body>{msg}</body></html>"

    # Prepare the report
    report = dict()
    # time
    report["date"] = str(datetime.date.today())
    report["time"] = str(datetime.datetime.now().time())[:8]
    # rankings
    def store_ranking(key, ranking):
        str_info = "<b>{0}</b> ({1}%, avg={2} min)"
        report[key] = "</li>\n<li>".join([str_info.format(*t) for t in ranking])

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
        print(f"Error while trying to write in '{cmd.report_path}' ({e})")
    else:
        print(f"Successfully wrote report {cmd.report_path}")

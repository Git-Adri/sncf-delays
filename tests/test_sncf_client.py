import json

from collector.sncf_client import extract_id_from_places_response, get_train_id_from_departure, \
    get_train_destination_from_departure, extract_disruption_id, parse_departures, \
    extract_base_departure_date_time_from_departure, extract_departure_date_time_from_departure, \
    extract_commercial_mode_from_departure


# Tests pour extract_id_from_places_response
def test_extract_id_from_places_response():
    expected_id = "stop_area:SNCF:87581009"

    with open('tests/fixtures/places/places-response.json', 'r') as fh:
        normal_response = json.load(fh)
        extracted_id = extract_id_from_places_response(normal_response)

        assert extracted_id == expected_id

def test_extract_id_from_places_response_no_id():

    with open('tests/fixtures/places/places-response-no-id.json', 'r') as fh:
        wrong_response = json.load(fh)
        extracted_id = extract_id_from_places_response(wrong_response)

        assert extracted_id is None

def test_extract_id_from_places_empty_response():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_response = json.load(fh)
        extracted_id = extract_id_from_places_response(wrong_response)

        assert extracted_id is None


# Tests pour get_train_id_from_departure
def test_get_train_id_from_departure():
    expected_train_id = "866224"

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        normal_departure = json.load(fh)
        extracted_train_id = get_train_id_from_departure(normal_departure)

        assert extracted_train_id == expected_train_id


def test_get_train_id_from_departure_no_id():

    with open('tests/fixtures/departures/departure-response-incomplete.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_id = get_train_id_from_departure(wrong_departure)

        assert extracted_train_id is None


def test_get_train_id_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_id = get_train_id_from_departure(wrong_departure)

        assert extracted_train_id is None


# Tests pour get_train_destination_from_departure
def test_get_train_destination_from_departure():
    expected_train_destination = "Coutras (Coutras)"

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        normal_departure = json.load(fh)
        extracted_train_destination = get_train_destination_from_departure(normal_departure)

        assert extracted_train_destination == expected_train_destination


def test_get_train_destination_from_departure_no_destination():

    with open('tests/fixtures/departures/departure-response-incomplete.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_destination = get_train_destination_from_departure(wrong_departure)

        assert extracted_train_destination is None


def test_get_train_destination_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_destination = get_train_destination_from_departure(wrong_departure)

        assert extracted_train_destination is None

# Tests pour extract_base_departure_date_time_from_departure
def test_extract_base_departure_date_time_from_departure():
    expected_base_departure_time = "20260922T120200"

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        normal_departure = json.load(fh)
        extracted_base_departure_time = extract_base_departure_date_time_from_departure(normal_departure)

        assert extracted_base_departure_time == expected_base_departure_time


def test_extract_base_departure_date_time_from_departure_no_destination():

    with open('tests/fixtures/departures/departure-response-incomplete.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_base_departure_time = extract_base_departure_date_time_from_departure(wrong_departure)

        assert extracted_base_departure_time is None


def test_extract_base_departure_date_time_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_base_departure_time = extract_base_departure_date_time_from_departure(wrong_departure)

        assert extracted_base_departure_time is None

# Tests pour extract_departure_date_time_from_departure
def test_extract_departure_date_time_from_departure():
    expected_departure_time = "20260922T130300"

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        normal_departure = json.load(fh)
        extracted_departure_time = extract_departure_date_time_from_departure(normal_departure)

        assert extracted_departure_time == expected_departure_time


def test_extract_departure_date_time_from_departure_no_destination():

    with open('tests/fixtures/departures/departure-response-incomplete.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_departure_time = extract_departure_date_time_from_departure(wrong_departure)

        assert extracted_departure_time is None


def test_extract_departure_date_time_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_departure_time = extract_departure_date_time_from_departure(wrong_departure)

        assert extracted_departure_time is None


# Tests pour extract_commercial_mode_from_departure
def test_extract_commercial_mode_from_departure():
    expected_commercial_mode = "TER NA"

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        normal_departure = json.load(fh)
        extracted_commercial_mode = extract_commercial_mode_from_departure(normal_departure)

        assert extracted_commercial_mode == expected_commercial_mode


def test_extract_commercial_mode_from_departure_no_destination():

    with open('tests/fixtures/departures/departure-response-incomplete.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_commercial_mode = extract_commercial_mode_from_departure(wrong_departure)

        assert extracted_commercial_mode is None


def test_extract_commercial_mode_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_commercial_mode = extract_commercial_mode_from_departure(wrong_departure)

        assert extracted_commercial_mode is None

# Test pour extract_link_id
def test_extract_link_id_if_disruption():

    with open('tests/fixtures/departures/departure-response-disruption.json', 'r') as fh:
        delayed_departure = json.load(fh)
        disruption_id = extract_disruption_id(delayed_departure)

        assert disruption_id == "b48ab4dc-4a72-4851-b6a1-a2bfab475d24"


def test_extract_link_id_if_no_disruption():

    with open('tests/fixtures/departures/departure-response.json', 'r') as fh:
        delayed_departure = json.load(fh)
        disruption_id = extract_disruption_id(delayed_departure)

        assert disruption_id is None


def test_extract_link_id_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        delayed_departure = json.load(fh)
        disruption_id = extract_disruption_id(delayed_departure)

        assert disruption_id is None


# Test parse departures
def test_parse_departures():

    expected_list = [{
        'base_departure_date_time': None,
        'departure_date_time': None,
        'headsign': '866153',
        'direction': 'Le Verdon (Le Verdon-sur-Mer)',
        'commercial_mode': 'TER NA',
        'disruption_id': None,
        'departure_station': 'Bordeaux'
    }, {
        'base_departure_date_time': '20260928T184400',
        'departure_date_time': '20260928T185400',
        'headsign': None,
        'direction': 'Hendaye (Hendaye)',
        'commercial_mode': 'TER NA',
        'disruption_id': '38db32fe-28e9-432a-b7f3-7ec2b6daaf9c',
        'departure_station': 'Bordeaux'
    }, {
        'base_departure_date_time': '20260928T185700',
        'departure_date_time': '20260928T185700',
        'headsign': '866875',
        'direction': None,
        'commercial_mode': 'TER NA',
        'disruption_id': None,
        'departure_station': 'Bordeaux'
    }, {
        'base_departure_date_time': '20260928T183300',
        'departure_date_time': '20260928T185800',
        'headsign': '866251',
        'direction': 'Arcachon (Arcachon)',
        'commercial_mode': None,
        'disruption_id': 'f97bb796-3a87-4314-a8a9-779f9dea9776',
        'departure_station': 'Bordeaux'
    }]

    with open('tests/fixtures/departures/all-departures.json', 'r') as fh:
        delayed_departure = json.load(fh)
        departure_list = parse_departures(delayed_departure, "Bordeaux")

    assert departure_list == expected_list

def test_parse_empty_departures():

    expected_list = []

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        delayed_departure = json.load(fh)
        departure_list = parse_departures(delayed_departure, "Bordeaux")

    assert departure_list == expected_list

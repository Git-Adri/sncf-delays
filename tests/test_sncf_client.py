import json

from collector.sncf_client import extract_id_from_places_response, get_train_id_from_departure, \
    get_train_destination_from_departure

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

    with open('tests/fixtures/departures/departure-response-no-train-id.json', 'r') as fh:
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

    with open('tests/fixtures/departures/departure-response-no-destination.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_destination = get_train_destination_from_departure(wrong_departure)

        assert extracted_train_destination is None


def test_get_train_destination_from_departure_empty():

    with open('tests/fixtures/empty-response.json', 'r') as fh:
        wrong_departure = json.load(fh)
        extracted_train_destination = get_train_destination_from_departure(wrong_departure)

        assert extracted_train_destination is None
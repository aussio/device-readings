import pytest
from werkzeug.test import Client
import device_reading.model as model
from app import app as main_app
from datetime import datetime


@pytest.fixture()
def app():
    main_app.config.update(
        {
            "TESTING": True,
        }
    )
    seed_cache()
    yield main_app
    # clear cache between tests
    model.cache = {}


@pytest.fixture()
def client(app) -> Client:
    return app.test_client()


def seed_cache():
    model.cache = {
        # Good format
        "36d5658a-6908-479e-887e-a949ec199272": {
            datetime.fromisoformat("2021-09-29T16:08:15+01:00"): 2,
            datetime.fromisoformat("2021-09-29T16:09:15+01:00"): 15,
        },
        # Bad data somehow
        "bad-data-in-these-parts": {
            "austin": 2,
        },
    }


get_reading_data = [
    # not found
    ("not-a-reading", 404),
    # found from test setup data
    ("36d5658a-6908-479e-887e-a949ec199272", 200),
    # bad data. 500 since somehow we let it already get in the cache.
    ("bad-data-in-these-parts", 500),
]


@pytest.mark.parametrize("id,status", get_reading_data)
def test_get_reading(id, status, client: Client):
    response = client.get(f"/reading/{id}")
    assert response.status_code == status


post_reading_data = [
    # New device id
    (
        {
            "id": "austins-cool-id",
            "readings": [
                {"timestamp": "2023-09-29T16:08:15+01:00", "count": 1337},
                {"timestamp": "2033-09-29T16:08:15+01:00", "count": 7.77},
                {"timestamp": "2043-09-29T16:08:15+01:00", "count": -10},
            ],
        },
        201,
        "austins-cool-id",
        200,
    ),
    # empty readings
    (
        {
            "id": "austins-cool-id-2",
            "readings": [],
        },
        201,
        "austins-cool-id-2",
        200,
    ),
    # bad readings
    (
        {
            "id": "austins-cool-id-3",
            "readings": [
                {"timestamp": "tomorrow", "count": 7},
            ],
        },
        400,
        "austins-cool-id-3",
        404,
    ),
    (
        {
            "missingID": "austins-cool-id-4",
            "readings": [
                {"timestamp": "2043-09-29T16:08:15+01:00", "count": 1337},
            ],
        },
        400,
        "austins-cool-id-4",
        404,
    ),
]


@pytest.mark.parametrize("data,post_status,id,get_status", post_reading_data)
def test_post_reading(data, post_status, id, get_status, client: Client):
    post_response = client.post(f"/reading", json=data)
    assert post_response.status_code == post_status
    # Assert the expected saving/not-saving of the data.
    get_response = client.get(f"/reading/{id}")
    assert get_response.status_code == get_status


def test_post_reading_duplicate_timestamp(client: Client):
    data = {
        # The existing ID in cache from test setup
        "id": "36d5658a-6908-479e-887e-a949ec199272",
        "readings": [
            # Existing timestamp #1, original count was 2. Should have count remain 2.
            {"timestamp": "2021-09-29T16:08:15+01:00", "count": 1337},
            # Existing timestamp #2 should remain there, untouched
            # {"timestamp": "2021-09-29T16:09:15+01:00", "count": 15},
            #
            # A new timestamp, which should be added
            {"timestamp": "2043-09-29T16:08:15+01:00", "count": -10},
        ],
    }
    post_response = client.post(f"/reading", json=data)
    assert post_response.status_code == 201
    # Assert the expected saving/not-saving of the data.
    get_response = client.get(f"/reading/36d5658a-6908-479e-887e-a949ec199272")
    assert get_response.status_code == 200
    expected_readings = [
        {"timestamp": "2043-09-29T16:08:15+01:00", "count": -10.0},
        {"timestamp": "2021-09-29T16:08:15+01:00", "count": 2.0},
        {"timestamp": "2021-09-29T16:09:15+01:00", "count": 15.0},
    ]
    # Sort response by count. An arbitrary sort to assert on list equality.
    # expected is already sorted by count above.
    actual_readings = sorted(
        get_response.get_json(force=True).get("readings", {}), key=lambda r: r["count"]
    )
    assert actual_readings == expected_readings

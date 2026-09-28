import json

from ecowatt.utils.session import _identity_from_cookie, _identity_from_query_params


def test_identity_cookie_round_trip_payload_is_valid():
    identity = {
        "user_id": "abc123",
        "user_name": "Ana",
        "class_group": "8A",
        "role": "Aluno",
        "age_group": "11-14",
        "gender": "Prefiro nao responder",
    }

    assert _identity_from_cookie(json.dumps(identity)) == identity


def test_invalid_identity_cookie_is_ignored():
    assert _identity_from_cookie("not-json") is None
    assert _identity_from_cookie(json.dumps({"user_id": "only-id"})) is None


def test_invalid_query_identity_is_ignored():
    assert _identity_from_query_params() is None

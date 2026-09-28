from ecowatt.services.participant_auth import normalize_username


def test_username_identity_is_normalized_before_becoming_participant_key():
    assert normalize_username("  Aluno_8A ") == "aluno_8a"

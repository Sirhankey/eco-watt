import pytest

from ecowatt.services.catalog_service import CatalogStore, create_personal_item, moderate_submission, submit_catalog_item


def appliance_payload(name="Ventilador"):
    return {"name": name, "category": "Sala", "power_watts": 80, "hours_per_day": 4, "days_per_month": 30}


def test_personal_item_duplicate_has_clear_error():
    store = CatalogStore()
    item = create_personal_item(store, "participant-1", "appliance", appliance_payload())
    assert item.participant_id == "participant-1"
    with pytest.raises(ValueError, match="ja foi criado"):
        create_personal_item(store, "participant-1", "appliance", appliance_payload(" ventilador "))


def test_submission_stays_pending_until_moderated_and_is_audited():
    store = CatalogStore()
    submission = submit_catalog_item(store, "participant-1", "appliance", appliance_payload(), "aluno-01")
    assert submission.status == "pending"
    assert submission.participant_id == "participant-1"
    moderated = moderate_submission(store, submission.id, "moderator-1", "approved")
    assert moderated.moderator_id == "moderator-1"
    assert store.moderation_audit[0]["decision"] == "approved"

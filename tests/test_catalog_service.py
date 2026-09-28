import pytest

from ecowatt.services.catalog_service import CatalogStore, create_personal_item, moderate_submission, submit_catalog_item


def appliance_payload(name="Ventilador"):
    return {"name": name, "category": "Sala", "power_watts": 80, "hours_per_day": 4, "days_per_month": 30}


def test_personal_item_duplicate_has_clear_error():
    store = CatalogStore()
    create_personal_item(store, "user-1", "appliance", appliance_payload())
    with pytest.raises(ValueError, match="ja foi criado"):
        create_personal_item(store, "user-1", "appliance", appliance_payload(" ventilador "))


def test_submission_stays_pending_until_moderated_and_is_audited():
    store = CatalogStore()
    submission = submit_catalog_item(store, "user-1", "appliance", appliance_payload(), "Ana")
    assert submission.status == "pending"
    moderated = moderate_submission(store, submission.id, "moderator-1", "approved")
    assert moderated.moderator_id == "moderator-1"
    assert store.moderation_audit[0]["decision"] == "approved"

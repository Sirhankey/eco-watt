from ecowatt.models.appliance import Appliance
from ecowatt.services.home_repository import ParticipantHomeRepository, home_to_appliances


class FakeSupabaseClient:
    def __init__(self):
        self.calls = []
        self.saved = None

    def request(self, method, table, *, filters=None, payload=None, prefer=None):
        self.calls.append((method, table, filters, payload, prefer))
        if method == "POST":
            self.saved = {"id": "home-1", **payload, "is_public": False}
            return 201, [self.saved]
        if filters and filters.get("is_public") == "eq.true":
            return 200, [self.saved] if self.saved and self.saved["is_public"] else []
        return 200, [self.saved] if self.saved else []


def test_save_home_upserts_snapshot_by_participant_id():
    client = FakeSupabaseClient()
    repository = ParticipantHomeRepository(client)
    appliances = [Appliance("lamp", "Lâmpada", 10, 5, 30, "Sala")]

    saved = repository.save_home("participant-1", "Casa da Ana", 0.85, ["Sala"], appliances)

    assert saved["participant_id"] == "participant-1"
    assert saved["rooms"] == ["Sala"]
    assert saved["monthly_kwh"] == 1.5
    assert client.calls[0][2] == {"on_conflict": "participant_id"}
    assert client.calls[0][4] == "resolution=merge-duplicates,return=representation"


def test_restore_home_snapshot_as_appliance_models():
    restored = home_to_appliances({
        "appliances": [{
            "id": "lamp",
            "name": "Lâmpada",
            "power_watts": 10,
            "hours_per_day": 5,
            "days_per_month": 30,
            "category": "Sala",
        }]
    })

    assert restored == [Appliance("lamp", "Lâmpada", 10, 5, 30, "Sala")]


def test_shared_home_listing_requests_only_admin_published_homes():
    client = FakeSupabaseClient()
    repository = ParticipantHomeRepository(client)

    assert repository.list_shared_homes() == []

    request = client.calls[-1]
    assert request[0] == "GET"
    assert request[2]["is_public"] == "eq.true"
import pytest

from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError


def test_private_repository_requires_server_side_service_key(monkeypatch):
    client = SupabaseServerClient()
    monkeypatch.setattr(client, "_secret", lambda name: None)

    with pytest.raises(SupabaseServerError, match="não está configurada"):
        client.request("GET", "participants", filters={"select": "id"})
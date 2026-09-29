"""Persistent participant homes and administrator-published shared scenarios."""
from dataclasses import asdict
from typing import Any

from ecowatt.models.appliance import Appliance
from ecowatt.services.energy_calculator import calculate_total_household_consumption
from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError


class HomeStorageUnavailable(RuntimeError):
    """Raised when participant home storage cannot be reached."""


class ParticipantHomeRepository:
    def __init__(self, client: SupabaseServerClient | None = None) -> None:
        self.client = client or SupabaseServerClient()

    def _request(self, method: str, **kwargs):
        try:
            return self.client.request(method, "participant_homes", **kwargs)
        except SupabaseServerError as error:
            raise HomeStorageUnavailable("Não foi possível acessar as casas salvas.") from error

    def save_home(
        self,
        participant_id: str,
        name: str,
        tariff: float,
        rooms: list[str],
        appliances: list[Appliance],
    ) -> dict[str, Any]:
        appliance_snapshot = [asdict(appliance) for appliance in appliances]
        monthly_kwh = calculate_total_household_consumption(appliances)["total_monthly_kwh"]
        status, rows = self._request(
            "POST",
            filters={"on_conflict": "participant_id"},
            payload={
                "participant_id": participant_id,
                "name": name.strip(),
                "tariff": tariff,
                "monthly_kwh": monthly_kwh,
                "rooms": rooms,
                "appliances": appliance_snapshot,
            },
            prefer="resolution=merge-duplicates,return=representation",
        )
        if status < 200 or status >= 300 or not rows:
            raise HomeStorageUnavailable("Não foi possível salvar sua residência.")
        return rows[0]

    def get_home(self, participant_id: str) -> dict[str, Any] | None:
        status, rows = self._request(
            "GET",
            filters={
                "select": "id,participant_id,name,tariff,monthly_kwh,rooms,appliances,is_public,updated_at",
                "participant_id": f"eq.{participant_id}",
                "limit": "1",
            },
        )
        if status < 200 or status >= 300:
            raise HomeStorageUnavailable("Não foi possível carregar sua residência salva.")
        return rows[0] if rows else None

    def list_shared_homes(self) -> list[dict[str, Any]]:
        status, rows = self._request(
            "GET",
            filters={
                "select": "id,participant_id,name,tariff,monthly_kwh,rooms,appliances,is_public,updated_at",
                "is_public": "eq.true",
                "order": "name.asc",
            },
        )
        if status < 200 or status >= 300:
            raise HomeStorageUnavailable("Não foi possível carregar os cenários compartilhados.")
        return rows or []


def home_to_appliances(home: dict[str, Any]) -> list[Appliance]:
    return [
        Appliance(
            id=str(item.get("id", "")),
            name=str(item["name"]),
            power_watts=float(item["power_watts"]),
            hours_per_day=float(item["hours_per_day"]),
            days_per_month=float(item.get("days_per_month", 30)),
            category=str(item.get("category", "Geral")),
            description=item.get("description"),
        )
        for item in home.get("appliances", [])
    ]
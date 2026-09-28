"""Domain models for official and user-owned catalog content."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class CatalogAppliance:
    id: str
    name: str
    category: str
    power_watts: float
    hours_per_day: float
    days_per_month: float = 30.0
    description: Optional[str] = None
    participant_id: Optional[str] = None
    status: str = "published"
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        from ecowatt.services.catalog_validation import validate_appliance_fields

        validate_appliance_fields(
            self.name,
            self.category,
            self.power_watts,
            self.hours_per_day,
            self.days_per_month,
            self.description,
        )


@dataclass
class CatalogPCComponent:
    id: str
    name: str
    category: str
    tdp_watts: float
    idle_watts: float
    typical_load_watts: float
    gaming_load_watts: float
    description: Optional[str] = None
    participant_id: Optional[str] = None
    status: str = "published"
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        from ecowatt.services.catalog_validation import validate_component_fields

        validate_component_fields(
            self.name,
            self.category,
            self.tdp_watts,
            self.idle_watts,
            self.typical_load_watts,
            self.gaming_load_watts,
            self.description,
        )


@dataclass
class CatalogFact:
    id: str
    title: str
    body: str
    participant_id: Optional[str] = None
    status: str = "published"


@dataclass
class CatalogPreset:
    id: str
    name: str
    description: Optional[str] = None
    participant_id: Optional[str] = None
    status: str = "published"
    items: list[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CatalogSubmission:
    id: str
    kind: str
    payload: Dict[str, Any]
    participant_id: str
    status: str = "pending"
    submitted_by_name: Optional[str] = None
    moderator_id: Optional[str] = None
    moderation_reason: Optional[str] = None

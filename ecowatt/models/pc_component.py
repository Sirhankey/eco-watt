"""Models for PC components and usage profile."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PCComponent:
    """Represents a PC hardware component with energy draw characteristics."""
    id: str
    name: str
    category: str
    tdp_watts: float
    idle_watts: float
    typical_load_watts: float
    gaming_load_watts: float
    description: Optional[str] = None

    def __post_init__(self):
        if any(w < 0 for w in [self.tdp_watts, self.idle_watts, self.typical_load_watts, self.gaming_load_watts]):
            raise ValueError("Os valores de potência/TDP não podem ser negativos.")


@dataclass
class PCUsageProfile:
    """Represents daily hours spent in different computing activities."""
    study_office_hours: float = 2.0
    gaming_heavy_hours: float = 3.0
    light_idle_hours: float = 2.0
    standby_off_hours: float = 17.0

    def __post_init__(self):
        total = self.study_office_hours + self.gaming_heavy_hours + self.light_idle_hours + self.standby_off_hours
        if any(h < 0 for h in [self.study_office_hours, self.gaming_heavy_hours, self.light_idle_hours, self.standby_off_hours]):
            raise ValueError("As horas de uso não podem ser negativas.")
        if round(total, 2) > 24.0:
            raise ValueError(f"O total de horas diárias ({total}h) não pode exceder 24h.")

    @property
    def total_active_hours(self) -> float:
        return self.study_office_hours + self.gaming_heavy_hours + self.light_idle_hours

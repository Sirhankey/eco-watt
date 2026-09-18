"""Models for appliances and energy items."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Appliance:
    """Represents an electrical appliance with its usage pattern."""
    id: str
    name: str
    power_watts: float
    hours_per_day: float
    days_per_month: float = 30.0
    category: str = "Geral"
    description: Optional[str] = None

    def __post_init__(self):
        if self.power_watts < 0:
            raise ValueError("A potência em Watts não pode ser negativa.")
        if self.hours_per_day < 0 or self.hours_per_day > 24:
            raise ValueError("As horas de uso por dia devem estar entre 0 e 24.")
        if self.days_per_month < 0 or self.days_per_month > 31:
            raise ValueError("Os dias de uso por mês devem estar entre 0 e 31.")

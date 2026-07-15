"""Framework-agnostic equipment domain objects.

These mirror the persisted Django models (apps.equipment.models) but carry
no ORM behavior. Converters living in the Django layer
(apps/equipment/services.py) build these from ORM instances before handing
off to pv_engine, per the "convert to dataclasses before calculating" rule.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ModuleTypeSpec:
    """A manufacturer PV module datasheet (STC ratings)."""

    manufacturer: str
    model: str
    pmax_w: Decimal
    vmpp_v: Decimal
    impp_a: Decimal
    voc_v: Decimal
    isc_a: Decimal
    temp_coeff_voc_pct_per_c: Decimal
    temp_coeff_isc_pct_per_c: Decimal
    temp_coeff_pmax_pct_per_c: Decimal
    max_system_voltage_v: Decimal
    series_fuse_rating_a: Decimal

    @property
    def label(self) -> str:
        return f"{self.manufacturer} {self.model}"


@dataclass(frozen=True)
class CableTypeSpec:
    """A cable/conductor catalog entry."""

    manufacturer: str
    material: str  # "copper" | "aluminum"
    conductor_size: str
    insulation_type: str
    ampacity_a: Decimal
    resistance_ohm_per_km: Decimal
    reactance_ohm_per_km: Decimal
    temp_rating_c: int
    voltage_rating_v: Decimal

    @property
    def label(self) -> str:
        return f"{self.manufacturer} {self.conductor_size} ({self.material})"


@dataclass(frozen=True)
class PCSTypeSpec:
    """A power conversion system (inverter/PCS) datasheet."""

    manufacturer: str
    model: str
    power_rating_kva: Decimal
    nominal_ac_voltage_v: Decimal
    min_dc_voltage_v: Decimal
    max_dc_voltage_v: Decimal
    mppt_min_voltage_v: Decimal
    mppt_max_voltage_v: Decimal
    max_dc_current_a: Decimal
    max_short_circuit_current_a: Decimal
    num_mppt: int
    efficiency_pct: Decimal

    @property
    def label(self) -> str:
        return f"{self.manufacturer} {self.model}"

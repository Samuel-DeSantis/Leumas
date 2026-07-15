import uuid
from decimal import Decimal

from ninja import Schema


class ModuleTypeOut(Schema):
    id: uuid.UUID
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


class ModuleTypeIn(Schema):
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


class CableTypeOut(Schema):
    id: uuid.UUID
    manufacturer: str
    material: str
    conductor_size: str
    insulation_type: str
    ampacity_a: Decimal
    resistance_ohm_per_km: Decimal
    reactance_ohm_per_km: Decimal
    temp_rating_c: int
    voltage_rating_v: Decimal


class CableTypeIn(Schema):
    manufacturer: str
    material: str
    conductor_size: str
    insulation_type: str
    ampacity_a: Decimal
    resistance_ohm_per_km: Decimal
    reactance_ohm_per_km: Decimal = Decimal("0")
    temp_rating_c: int
    voltage_rating_v: Decimal


class PCSTypeOut(Schema):
    id: uuid.UUID
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
    has_integrated_transformer: bool


class PCSTypeIn(Schema):
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
    num_mppt: int = 1
    efficiency_pct: Decimal
    has_integrated_transformer: bool = False

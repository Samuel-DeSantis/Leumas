"""Equipment library: manufacturer equipment *definitions*.

Rule (CLAUDE.md): "Separate Equipment Definition from Equipment Instance."
These models are the definitions (catalog/datasheet entries). Instances
(e.g. an installed PCS, a physical string) live in apps.electrical and
reference these by foreign key.

Each equipment type is scoped to an Organization: every org curates its own
library. (A shared cross-organization manufacturer catalog is a natural
future enhancement, but is out of scope for Phase 1 -- see README design
notes.)

Rule: models exist primarily for persistence. Engineering sanity checks
run through pv_engine.validation.equipment and are invoked from forms
(apps/equipment/forms.py) via apps/equipment/services.py converters.
"""

from django.db import models

from apps.core.models import BaseModel
from apps.organizations.models import Organization


class ModuleType(BaseModel):
    """A PV module manufacturer datasheet (STC ratings)."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="module_types")
    manufacturer = models.CharField(max_length=150)
    model = models.CharField(max_length=150)

    pmax_w = models.DecimalField("Pmax (W)", max_digits=8, decimal_places=2)
    vmpp_v = models.DecimalField("Vmpp (V)", max_digits=7, decimal_places=3)
    impp_a = models.DecimalField("Impp (A)", max_digits=7, decimal_places=3)
    voc_v = models.DecimalField("Voc (V)", max_digits=7, decimal_places=3)
    isc_a = models.DecimalField("Isc (A)", max_digits=7, decimal_places=3)

    temp_coeff_voc_pct_per_c = models.DecimalField(
        "Temp. coefficient of Voc (%/\u00b0C)", max_digits=6, decimal_places=4
    )
    temp_coeff_isc_pct_per_c = models.DecimalField(
        "Temp. coefficient of Isc (%/\u00b0C)", max_digits=6, decimal_places=4
    )
    temp_coeff_pmax_pct_per_c = models.DecimalField(
        "Temp. coefficient of Pmax (%/\u00b0C)", max_digits=6, decimal_places=4
    )

    length_mm = models.PositiveIntegerField(null=True, blank=True)
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    depth_mm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    max_system_voltage_v = models.DecimalField("Max. system voltage (V)", max_digits=7, decimal_places=2)
    series_fuse_rating_a = models.DecimalField("Series fuse rating (A)", max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["manufacturer", "model"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "manufacturer", "model"], name="unique_module_type_per_org"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model}"


class CableType(BaseModel):
    """A cable/conductor catalog entry."""

    class Material(models.TextChoices):
        COPPER = "copper", "Copper"
        ALUMINUM = "aluminum", "Aluminum"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="cable_types")
    manufacturer = models.CharField(max_length=150)
    material = models.CharField(max_length=20, choices=Material.choices)
    conductor_size = models.CharField(max_length=50, help_text="e.g. '4/0 AWG', '500 kcmil', '95 mm\u00b2'")
    insulation_type = models.CharField(max_length=50, help_text="e.g. XLPE, THWN-2")

    ampacity_a = models.DecimalField("Ampacity (A)", max_digits=7, decimal_places=2)
    resistance_ohm_per_km = models.DecimalField(max_digits=9, decimal_places=5)
    reactance_ohm_per_km = models.DecimalField(max_digits=9, decimal_places=5, default=0)
    temp_rating_c = models.PositiveSmallIntegerField(help_text="Conductor temperature rating, \u00b0C")
    voltage_rating_v = models.DecimalField(max_digits=8, decimal_places=2)

    cost_per_meter = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="Reserved for future cost estimation."
    )

    class Meta:
        ordering = ["manufacturer", "conductor_size"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "manufacturer", "conductor_size", "material", "insulation_type"],
                name="unique_cable_type_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.conductor_size} ({self.get_material_display()})"


class PCSType(BaseModel):
    """A power conversion system (inverter / PCS) datasheet."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="pcs_types")
    manufacturer = models.CharField(max_length=150)
    model = models.CharField(max_length=150)

    power_rating_kva = models.DecimalField("Power rating (kVA)", max_digits=8, decimal_places=2)
    nominal_ac_voltage_v = models.DecimalField(max_digits=7, decimal_places=2)
    min_dc_voltage_v = models.DecimalField(max_digits=7, decimal_places=2)
    max_dc_voltage_v = models.DecimalField(max_digits=7, decimal_places=2)
    mppt_min_voltage_v = models.DecimalField(max_digits=7, decimal_places=2)
    mppt_max_voltage_v = models.DecimalField(max_digits=7, decimal_places=2)
    max_dc_current_a = models.DecimalField(max_digits=7, decimal_places=2)
    max_short_circuit_current_a = models.DecimalField(max_digits=7, decimal_places=2)
    num_mppt = models.PositiveSmallIntegerField(default=1)
    efficiency_pct = models.DecimalField("Efficiency (%)", max_digits=5, decimal_places=2)

    has_integrated_transformer = models.BooleanField(default=False)

    class Meta:
        ordering = ["manufacturer", "model"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "manufacturer", "model"], name="unique_pcs_type_per_org"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model}"

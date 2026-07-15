"""Electrical hierarchy: Site -> PCSInstance -> DCCircuit -> String,
plus Site -> Substation / MVCircuit, and Project -> POI.

Rule (CLAUDE.md): "Separate Equipment Definition from Equipment Instance."
Everything here is an *instance* of equipment placed into a real project;
the definitions (datasheets) live in apps.equipment.

Design note on Combiner boxes: ROADMAP.md marks Combiner boxes as a
Phase 2 "placeholder" equipment type, but the hierarchy diagram in
Claude_Development_Specification shows String -> Combiner -> DC Circuit.
Modeling a full Combiner *instance* table now would add a layer with no
equipment definition behind it yet. Instead, String carries an optional
free-text ``combiner_identifier`` so designs that group strings through
combiner boxes can record that grouping today; a proper Combiner
model (with a CombinerType definition) can replace this field with a real
foreign key in Phase 2 without changing the rest of the hierarchy.

No calculated values are stored anywhere in this file (Rule: derive,
don't duplicate) -- only counts/identifiers/references needed to describe
the physical design.
"""

from django.db import models

from apps.core.models import BaseModel
from apps.equipment.models import ModuleType, PCSType
from apps.projects.models import Project


class Site(BaseModel):
    """A physical site within a project. Most projects have exactly one,
    but multi-site projects (e.g. phased builds) are supported.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["project", "name"], name="unique_site_name_per_project"),
        ]

    def __str__(self) -> str:
        return self.name


class PCSInstance(BaseModel):
    """An installed inverter/PCS unit."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="pcs_instances")
    pcs_type = models.ForeignKey(PCSType, on_delete=models.PROTECT, related_name="instances")
    identifier = models.CharField(max_length=100, help_text="e.g. 'INV-01', 'PCS-A1'")

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.UniqueConstraint(fields=["site", "identifier"], name="unique_pcs_identifier_per_site"),
        ]

    def __str__(self) -> str:
        return self.identifier


class DCCircuit(BaseModel):
    """A DC input circuit into a PCS (typically one MPPT channel)."""

    pcs_instance = models.ForeignKey(PCSInstance, on_delete=models.CASCADE, related_name="dc_circuits")
    identifier = models.CharField(max_length=100, help_text="e.g. 'MPPT-1'")
    mppt_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.UniqueConstraint(
                fields=["pcs_instance", "identifier"], name="unique_dc_circuit_identifier_per_pcs"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.pcs_instance.identifier} / {self.identifier}"


class String(BaseModel):
    """A series string of modules of a single ModuleType.

    No physical per-module rows are stored: at utility scale a plant can
    have hundreds of thousands of individual modules, and every module in
    a string is electrically identical and interchangeable for modeling
    purposes. Storing ``modules_per_string`` + a ModuleType reference is
    the single source of truth (Rule: avoid duplicated data, derive rather
    than store) and is what Phase 5's string-sizing calculations will
    consume directly.
    """

    dc_circuit = models.ForeignKey(DCCircuit, on_delete=models.CASCADE, related_name="strings")
    module_type = models.ForeignKey(ModuleType, on_delete=models.PROTECT, related_name="strings")
    identifier = models.CharField(max_length=100, help_text="e.g. 'STR-1'")
    modules_per_string = models.PositiveIntegerField()
    combiner_identifier = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional label for the combiner box this string is wired through, if any.",
    )

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.UniqueConstraint(
                fields=["dc_circuit", "identifier"], name="unique_string_identifier_per_dc_circuit"
            ),
        ]

    def __str__(self) -> str:
        return self.identifier


class Substation(BaseModel):
    """Placeholder substation record (full equipment modeling: Phase 2+)."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="substations")
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["site", "name"], name="unique_substation_name_per_site"),
        ]

    def __str__(self) -> str:
        return self.name


class MVCircuit(BaseModel):
    """A medium-voltage collection circuit linking one or more PCS
    instances to a substation.
    """

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="mv_circuits")
    identifier = models.CharField(max_length=100, help_text="e.g. 'MV-CKT-1'")
    voltage_kv = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    substation = models.ForeignKey(
        Substation, on_delete=models.SET_NULL, null=True, blank=True, related_name="mv_circuits"
    )
    pcs_instances = models.ManyToManyField(PCSInstance, related_name="mv_circuits", blank=True)

    class Meta:
        ordering = ["identifier"]
        constraints = [
            models.UniqueConstraint(fields=["site", "identifier"], name="unique_mv_circuit_identifier_per_site"),
        ]

    def __str__(self) -> str:
        return self.identifier


class POI(BaseModel):
    """Point of Interconnection: where the project connects to the grid."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pois")
    name = models.CharField(max_length=200)
    voltage_kv = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    utility_name = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "POI"
        verbose_name_plural = "POIs"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["project", "name"], name="unique_poi_name_per_project"),
        ]

    def __str__(self) -> str:
        return self.name

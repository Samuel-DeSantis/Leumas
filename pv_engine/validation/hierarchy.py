"""Structural validation of the electrical hierarchy.

Phase 1 scope, per ROADMAP.md: "Validation of connections" -- not
electrical calculations. This checks that the model is well-formed:
unique identifiers within their scope, no cross-organization equipment
references, and sane quantities (e.g. modules_per_string > 0).

Full engineering validation (overloads, invalid voltages/currents, missing
required data) is Phase 7's Validation Engine; this module is the
foundation it will build on.
"""

from collections import Counter

from pv_engine.electrical.domain import ElectricalHierarchySpec, SiteSpec

from .base import ValidationResult


def _check_unique(result: ValidationResult, identifiers: list[str], scope: str, code_prefix: str) -> None:
    counts = Counter(identifiers)
    for identifier, count in counts.items():
        if count > 1:
            result.error(
                f"{code_prefix}.duplicate_identifier",
                f"Identifier '{identifier}' is used {count} times within {scope}.",
                scope,
            )


def _validate_site(result: ValidationResult, site: SiteSpec, organization_id: str) -> None:
    _check_unique(
        result,
        [pcs.identifier for pcs in site.pcs_instances],
        f"Site '{site.name}'",
        "pcs_instance",
    )

    for pcs in site.pcs_instances:
        if pcs.pcs_type_organization_id != organization_id:
            result.error(
                "pcs_instance.cross_organization_equipment",
                f"PCS instance '{pcs.identifier}' references a PCS type from a different organization.",
                f"PCSInstance '{pcs.identifier}'",
            )

        _check_unique(
            result,
            [dc.identifier for dc in pcs.dc_circuits],
            f"PCS '{pcs.identifier}'",
            "dc_circuit",
        )

        for dc in pcs.dc_circuits:
            _check_unique(
                result,
                [s.identifier for s in dc.strings],
                f"DC circuit '{dc.identifier}'",
                "string",
            )
            for string in dc.strings:
                if string.modules_per_string <= 0:
                    result.error(
                        "string.invalid_module_count",
                        f"String '{string.identifier}' must have at least 1 module "
                        f"(got {string.modules_per_string}).",
                        f"String '{string.identifier}'",
                    )
                if string.module_type_organization_id != organization_id:
                    result.error(
                        "string.cross_organization_equipment",
                        f"String '{string.identifier}' references a module type from a "
                        "different organization.",
                        f"String '{string.identifier}'",
                    )

    _check_unique(
        result,
        [sub.name for sub in site.substations],
        f"Site '{site.name}'",
        "substation",
    )

    pcs_ids_in_site = {pcs.id for pcs in site.pcs_instances}
    substation_ids_in_site = {sub.id for sub in site.substations}

    _check_unique(
        result,
        [mv.identifier for mv in site.mv_circuits],
        f"Site '{site.name}'",
        "mv_circuit",
    )

    for mv in site.mv_circuits:
        if not mv.pcs_instance_ids:
            result.warning(
                "mv_circuit.no_pcs_instances",
                f"MV circuit '{mv.identifier}' is not connected to any PCS instance yet.",
                f"MVCircuit '{mv.identifier}'",
            )
        for pcs_id in mv.pcs_instance_ids:
            if pcs_id not in pcs_ids_in_site:
                result.error(
                    "mv_circuit.pcs_instance_not_in_site",
                    f"MV circuit '{mv.identifier}' references a PCS instance outside this site.",
                    f"MVCircuit '{mv.identifier}'",
                )
        if mv.substation_id is not None and mv.substation_id not in substation_ids_in_site:
            result.error(
                "mv_circuit.substation_not_in_site",
                f"MV circuit '{mv.identifier}' references a substation outside this site.",
                f"MVCircuit '{mv.identifier}'",
            )


def validate_electrical_hierarchy(hierarchy: ElectricalHierarchySpec) -> ValidationResult:
    """Validate an entire project's electrical hierarchy.

    Returns a ValidationResult; ``result.is_valid`` is False if any
    ERROR-level issue was found. WARNING-level issues do not block saving
    but should be surfaced to the engineer.
    """
    result = ValidationResult()

    _check_unique(
        result,
        [site.name for site in hierarchy.sites],
        f"Project {hierarchy.project_id}",
        "site",
    )
    _check_unique(
        result,
        [poi.name for poi in hierarchy.pois],
        f"Project {hierarchy.project_id}",
        "poi",
    )

    for site in hierarchy.sites:
        _validate_site(result, site, hierarchy.organization_id)

    return result

from pv_engine.electrical.domain import (
    DCCircuitSpec,
    ElectricalHierarchySpec,
    MVCircuitSpec,
    PCSInstanceSpec,
    POISpec,
    SiteSpec,
    StringSpec,
    SubstationSpec,
)
from pv_engine.validation.hierarchy import validate_electrical_hierarchy

ORG = "org-1"
OTHER_ORG = "org-2"


def _simple_hierarchy(
    sites: tuple[SiteSpec, ...] | None = None,
    pois: tuple[POISpec, ...] | None = None,
) -> ElectricalHierarchySpec:
    string = StringSpec(
        id="string-1",
        identifier="STR-1",
        module_type_id="module-1",
        module_type_organization_id=ORG,
        modules_per_string=28,
    )
    dc_circuit = DCCircuitSpec(id="dc-1", identifier="MPPT-1", strings=(string,))
    pcs_instance = PCSInstanceSpec(
        id="pcs-1",
        identifier="INV-01",
        pcs_type_id="pcs-type-1",
        pcs_type_organization_id=ORG,
        dc_circuits=(dc_circuit,),
    )
    substation = SubstationSpec(id="sub-1", name="Substation A")
    mv_circuit = MVCircuitSpec(
        id="mv-1",
        identifier="MV-1",
        voltage_kv="34.5",
        pcs_instance_ids=("pcs-1",),
        substation_id="sub-1",
    )
    default_site = SiteSpec(
        id="site-1",
        name="Site A",
        pcs_instances=(pcs_instance,),
        mv_circuits=(mv_circuit,),
        substations=(substation,),
    )
    default_pois = (POISpec(id="poi-1", name="POI A"),)
    return ElectricalHierarchySpec(
        project_id="project-1",
        organization_id=ORG,
        sites=sites if sites is not None else (default_site,),
        pois=pois if pois is not None else default_pois,
    )


def test_well_formed_hierarchy_is_valid():
    result = validate_electrical_hierarchy(_simple_hierarchy())
    assert result.is_valid, [i.message for i in result.errors]


def test_duplicate_site_names_is_error():
    site = _simple_hierarchy().sites[0]
    hierarchy = _simple_hierarchy(sites=(site, site))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "site.duplicate_identifier" for i in result.errors)


def test_duplicate_string_identifiers_within_dc_circuit_is_error():
    hierarchy = _simple_hierarchy()
    dc_circuit = hierarchy.sites[0].pcs_instances[0].dc_circuits[0]
    duplicated_dc = DCCircuitSpec(
        id=dc_circuit.id, identifier=dc_circuit.identifier, strings=(dc_circuit.strings[0], dc_circuit.strings[0])
    )
    pcs_instance = hierarchy.sites[0].pcs_instances[0]
    new_pcs = PCSInstanceSpec(
        id=pcs_instance.id,
        identifier=pcs_instance.identifier,
        pcs_type_id=pcs_instance.pcs_type_id,
        pcs_type_organization_id=pcs_instance.pcs_type_organization_id,
        dc_circuits=(duplicated_dc,),
    )
    new_site = SiteSpec(id="site-1", name="Site A", pcs_instances=(new_pcs,))
    hierarchy = _simple_hierarchy(sites=(new_site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "string.duplicate_identifier" for i in result.errors)


def test_string_with_zero_modules_is_error():
    hierarchy = _simple_hierarchy()
    bad_string = StringSpec(
        id="string-1",
        identifier="STR-1",
        module_type_id="module-1",
        module_type_organization_id=ORG,
        modules_per_string=0,
    )
    dc_circuit = DCCircuitSpec(id="dc-1", identifier="MPPT-1", strings=(bad_string,))
    pcs_instance = PCSInstanceSpec(
        id="pcs-1",
        identifier="INV-01",
        pcs_type_id="pcs-type-1",
        pcs_type_organization_id=ORG,
        dc_circuits=(dc_circuit,),
    )
    site = SiteSpec(id="site-1", name="Site A", pcs_instances=(pcs_instance,))
    hierarchy = _simple_hierarchy(sites=(site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "string.invalid_module_count" for i in result.errors)


def test_cross_organization_module_type_is_error():
    hierarchy = _simple_hierarchy()
    bad_string = StringSpec(
        id="string-1",
        identifier="STR-1",
        module_type_id="module-1",
        module_type_organization_id=OTHER_ORG,
        modules_per_string=28,
    )
    dc_circuit = DCCircuitSpec(id="dc-1", identifier="MPPT-1", strings=(bad_string,))
    pcs_instance = PCSInstanceSpec(
        id="pcs-1",
        identifier="INV-01",
        pcs_type_id="pcs-type-1",
        pcs_type_organization_id=ORG,
        dc_circuits=(dc_circuit,),
    )
    site = SiteSpec(id="site-1", name="Site A", pcs_instances=(pcs_instance,))
    hierarchy = _simple_hierarchy(sites=(site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "string.cross_organization_equipment" for i in result.errors)


def test_cross_organization_pcs_type_is_error():
    hierarchy = _simple_hierarchy()
    pcs_instance = hierarchy.sites[0].pcs_instances[0]
    bad_pcs = PCSInstanceSpec(
        id=pcs_instance.id,
        identifier=pcs_instance.identifier,
        pcs_type_id=pcs_instance.pcs_type_id,
        pcs_type_organization_id=OTHER_ORG,
        dc_circuits=pcs_instance.dc_circuits,
    )
    site = SiteSpec(id="site-1", name="Site A", pcs_instances=(bad_pcs,))
    hierarchy = _simple_hierarchy(sites=(site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "pcs_instance.cross_organization_equipment" for i in result.errors)


def test_mv_circuit_referencing_pcs_outside_site_is_error():
    site = SiteSpec(
        id="site-1",
        name="Site A",
        mv_circuits=(MVCircuitSpec(id="mv-1", identifier="MV-1", voltage_kv="34.5", pcs_instance_ids=("ghost-pcs",)),),
    )
    hierarchy = _simple_hierarchy(sites=(site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "mv_circuit.pcs_instance_not_in_site" for i in result.errors)


def test_mv_circuit_with_no_pcs_instances_is_warning():
    site = SiteSpec(
        id="site-1",
        name="Site A",
        mv_circuits=(MVCircuitSpec(id="mv-1", identifier="MV-1", voltage_kv="34.5", pcs_instance_ids=()),),
    )
    hierarchy = _simple_hierarchy(sites=(site,))
    result = validate_electrical_hierarchy(hierarchy)
    assert result.is_valid
    assert any(i.code == "mv_circuit.no_pcs_instances" for i in result.warnings)


def test_duplicate_poi_names_is_error():
    poi = POISpec(id="poi-1", name="POI A")
    hierarchy = _simple_hierarchy(pois=(poi, poi))
    result = validate_electrical_hierarchy(hierarchy)
    assert not result.is_valid
    assert any(i.code == "poi.duplicate_identifier" for i in result.errors)

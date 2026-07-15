import pytest
from django.db import IntegrityError

from apps.electrical.models import DCCircuit, PCSInstance, Site, String

pytestmark = pytest.mark.django_db


def test_site_name_unique_per_project(project, site):
    with pytest.raises(IntegrityError):
        Site.objects.create(project=project, name=site.name)


def test_pcs_instance_identifier_unique_per_site(site, pcs_instance, pcs_type):
    with pytest.raises(IntegrityError):
        PCSInstance.objects.create(site=site, pcs_type=pcs_type, identifier=pcs_instance.identifier)


def test_dc_circuit_identifier_unique_per_pcs_instance(pcs_instance, dc_circuit):
    with pytest.raises(IntegrityError):
        DCCircuit.objects.create(pcs_instance=pcs_instance, identifier=dc_circuit.identifier)


def test_string_identifier_unique_per_dc_circuit(dc_circuit, string_obj, module_type):
    with pytest.raises(IntegrityError):
        String.objects.create(
            dc_circuit=dc_circuit,
            module_type=module_type,
            identifier=string_obj.identifier,
            modules_per_string=10,
        )


def test_module_type_cannot_be_deleted_while_referenced(module_type, string_obj):
    from django.db.models import ProtectedError

    with pytest.raises(ProtectedError):
        module_type.delete()

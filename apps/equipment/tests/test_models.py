from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.equipment.models import ModuleType

pytestmark = pytest.mark.django_db


def test_module_type_str(module_type):
    assert str(module_type) == "JinkoSolar Tiger Neo 585"


def test_module_type_unique_per_org(organization, module_type):
    with pytest.raises(IntegrityError):
        ModuleType.objects.create(
            organization=organization,
            manufacturer=module_type.manufacturer,
            model=module_type.model,
            pmax_w=Decimal("500"),
            vmpp_v=Decimal("30"),
            impp_a=Decimal("15"),
            voc_v=Decimal("38"),
            isc_a=Decimal("16"),
            temp_coeff_voc_pct_per_c=Decimal("-0.25"),
            temp_coeff_isc_pct_per_c=Decimal("0.04"),
            temp_coeff_pmax_pct_per_c=Decimal("-0.29"),
            max_system_voltage_v=Decimal("1500"),
            series_fuse_rating_a=Decimal("20"),
        )


def test_module_type_same_model_different_org_allowed(module_type):
    from apps.organizations.models import Organization

    other_org = Organization.objects.create(name="Other Co")
    ModuleType.objects.create(
        organization=other_org,
        manufacturer=module_type.manufacturer,
        model=module_type.model,
        pmax_w=module_type.pmax_w,
        vmpp_v=module_type.vmpp_v,
        impp_a=module_type.impp_a,
        voc_v=module_type.voc_v,
        isc_a=module_type.isc_a,
        temp_coeff_voc_pct_per_c=module_type.temp_coeff_voc_pct_per_c,
        temp_coeff_isc_pct_per_c=module_type.temp_coeff_isc_pct_per_c,
        temp_coeff_pmax_pct_per_c=module_type.temp_coeff_pmax_pct_per_c,
        max_system_voltage_v=module_type.max_system_voltage_v,
        series_fuse_rating_a=module_type.series_fuse_rating_a,
    )
    assert ModuleType.objects.filter(model=module_type.model).count() == 2

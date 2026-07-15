from django.contrib import admin

from .models import POI, DCCircuit, MVCircuit, PCSInstance, Site, String, Substation


class PCSInstanceInline(admin.TabularInline):
    model = PCSInstance
    extra = 0


class SubstationInline(admin.TabularInline):
    model = Substation
    extra = 0


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ["name", "project"]
    list_filter = ["project__organization"]
    inlines = [PCSInstanceInline, SubstationInline]


@admin.register(PCSInstance)
class PCSInstanceAdmin(admin.ModelAdmin):
    list_display = ["identifier", "site", "pcs_type"]
    list_filter = ["site__project__organization"]


@admin.register(DCCircuit)
class DCCircuitAdmin(admin.ModelAdmin):
    list_display = ["identifier", "pcs_instance", "mppt_number"]


@admin.register(String)
class StringAdmin(admin.ModelAdmin):
    list_display = ["identifier", "dc_circuit", "module_type", "modules_per_string"]


@admin.register(Substation)
class SubstationAdmin(admin.ModelAdmin):
    list_display = ["name", "site"]


@admin.register(MVCircuit)
class MVCircuitAdmin(admin.ModelAdmin):
    list_display = ["identifier", "site", "substation", "voltage_kv"]


@admin.register(POI)
class POIAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "voltage_kv", "utility_name"]

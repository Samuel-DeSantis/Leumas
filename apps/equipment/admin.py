from django.contrib import admin

from .models import CableType, ModuleType, PCSType


@admin.register(ModuleType)
class ModuleTypeAdmin(admin.ModelAdmin):
    list_display = ["manufacturer", "model", "organization", "pmax_w", "vmpp_v", "voc_v"]
    list_filter = ["organization", "manufacturer"]
    search_fields = ["manufacturer", "model"]


@admin.register(CableType)
class CableTypeAdmin(admin.ModelAdmin):
    list_display = ["manufacturer", "conductor_size", "material", "organization", "ampacity_a"]
    list_filter = ["organization", "material"]
    search_fields = ["manufacturer", "conductor_size"]


@admin.register(PCSType)
class PCSTypeAdmin(admin.ModelAdmin):
    list_display = ["manufacturer", "model", "organization", "power_rating_kva", "num_mppt"]
    list_filter = ["organization", "manufacturer"]
    search_fields = ["manufacturer", "model"]

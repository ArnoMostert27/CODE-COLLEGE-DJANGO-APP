from django.contrib import admin

from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "property_type",
        "suburb",
        "purchase_price",
        "monthly_rent",
        "created_at",
    )
    list_filter = ("property_type", "city")
    search_fields = ("name", "suburb", "city")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Property", {
            "fields": (
                "owner",
                "name",
                "property_type",
                ("suburb", "city"),
                ("bedrooms", "bathrooms", "floor_size_sqm"),
            )
        }),
        ("Purchase & financing", {
            "fields": (
                "purchase_price",
                "deposit",
                ("interest_rate", "loan_term_years"),
            )
        }),
        ("Income", {
            "fields": (
                "monthly_rent",
                ("vacancy_rate", "annual_rent_growth"),
            )
        }),
        ("Operating expenses (monthly)", {
            "fields": (
                ("monthly_levies", "monthly_rates"),
                ("monthly_insurance", "monthly_maintenance"),
                "management_fee_percent",
            )
        }),
        ("Projection", {
            "fields": (("annual_appreciation", "holding_period_years"),),
        }),
        ("Meta", {
            "fields": (("created_at", "updated_at"),),
            "classes": ("collapse",),
        }),
    )
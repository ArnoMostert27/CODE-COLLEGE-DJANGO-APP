from django.conf import settings
from django.db import models


class Deal(models.Model):
    """A property analysed as an investment, with its base-case assumptions."""

    class PropertyType(models.TextChoices):
        HOUSE = "house", "House"
        APARTMENT = "apartment", "Apartment"
        TOWNHOUSE = "townhouse", "Townhouse"
        DUPLEX = "duplex", "Duplex"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deals",
    )
    name = models.CharField(max_length=120)
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
    )
    suburb = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    floor_size_sqm = models.PositiveIntegerField(null=True, blank=True)

    # Purchase & financing
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Annual bond interest rate, %"
    )
    loan_term_years = models.PositiveSmallIntegerField(default=20)

    # Income
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    vacancy_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=5, help_text="Expected vacancy, %"
    )
    annual_rent_growth = models.DecimalField(
        max_digits=5, decimal_places=2, default=5, help_text="%"
    )

    # Monthly operating expenses
    monthly_levies = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_rates = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_maintenance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    management_fee_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="% of monthly rent"
    )

    # Projection assumptions
    annual_appreciation = models.DecimalField(
        max_digits=5, decimal_places=2, default=6, help_text="Capital growth, %"
    )
    holding_period_years = models.PositiveSmallIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def loan_amount(self):
        return self.purchase_price - self.deposit
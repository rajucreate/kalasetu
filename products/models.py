from django.db import models
from django.conf import settings


class Product(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    artisan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ARTISAN'},
        related_name="products"
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(upload_to="product_images/")

    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Cultural Story Fields
    region = models.CharField(
        max_length=255,
        blank=True,
        help_text="Geographic region or origin of the craft"
    )
    cultural_story = models.TextField(
        blank=True,
        help_text="The story behind this craft and its cultural significance"
    )
    craft_process = models.TextField(
        blank=True,
        help_text="Step-by-step explanation of how this product is made"
    )

    # Verification & Impact
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        help_text="Consultant verification status"
    )
    impact_score = models.IntegerField(
        default=0,
        help_text="Social impact score (0-100) representing artisan empowerment"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this product has been verified by a cultural consultant"
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_products",
        limit_choices_to={'role': 'CONSULTANT'},
        help_text="Cultural consultant who verified this product"
    )
    verification_note = models.TextField(
        blank=True,
        help_text="Consultant note for verification or rejection"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When verification decision was made"
    )

    def __str__(self):
        return self.name
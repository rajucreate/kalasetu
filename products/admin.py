from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "artisan", "price", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "artisan__email")
    ordering = ("-created_at",)
from django.urls import path
from .views import (
    landing_page,
    admin_dashboard,
    approve_product,
    reject_product,
    artisan_dashboard,
    buyer_dashboard,
    consultant_dashboard,
)

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("approve-product/<int:product_id>/", approve_product, name="approve_product"),
    path("reject-product/<int:product_id>/", reject_product, name="reject_product"),
    path("artisan-dashboard/", artisan_dashboard, name="artisan_dashboard"),
    path("buyer-dashboard/", buyer_dashboard, name="buyer_dashboard"),
    path("consultant-dashboard/", consultant_dashboard, name="consultant_dashboard"),
]
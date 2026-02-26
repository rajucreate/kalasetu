from django.urls import path
from .views import (
    upload_product,
    product_list,
    product_detail,
    add_to_cart,
    view_cart,
    checkout,
)

urlpatterns = [
    path("marketplace/", product_list, name="product_list"),
    path("products/<int:pk>/", product_detail, name="product_detail"),
    path("upload-product/", upload_product, name="upload_product"),
    path("add-to-cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", view_cart, name="view_cart"),
    path("checkout/", checkout, name="checkout"),
]
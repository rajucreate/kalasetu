from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product


@login_required
def upload_product(request):
    if request.user.role != "ARTISAN":
        return redirect("login")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan = request.user
            product.save()
            return redirect("artisan_dashboard")
    else:
        form = ProductForm()

    return render(request, "products/upload_product.html", {"form": form})


def product_list(request):
    products = Product.objects.filter(
        is_approved=True
    ).exclude(
        verification_status=Product.VerificationStatus.REJECTED
    ).order_by("-created_at")
    return render(request, "products/product_list.html", {"products": products})


def product_detail(request, pk):
    """
    Display detailed product information with cultural journey, verification, and impact.
    Handles Add to Cart functionality.
    """
    product = get_object_or_404(
        Product.objects.filter(is_approved=True).exclude(
            verification_status=Product.VerificationStatus.REJECTED
        ),
        id=pk,
    )

    # Handle Add to Cart (POST)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to add items to your cart.")
            next_url = quote(request.get_full_path())
            return redirect(f"{reverse('login')}?next={next_url}")

        cart = request.session.get("cart", {})

        if str(pk) in cart:
            cart[str(pk)] += 1
        else:
            cart[str(pk)] = 1

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(request, f"{product.name} added to cart!")
        return redirect("product_detail", pk=pk)

    context = {
        "product": product,
        "cart_count": len(request.session.get("cart", {}))
    }

    return render(request, "products/product_detail.html", context)


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to add items to your cart.")
        next_url = quote(request.get_full_path())
        return redirect(f"{reverse('login')}?next={next_url}")

    product = get_object_or_404(Product, id=product_id, is_approved=True)

    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("product_list")


def view_cart(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.subtotal = product.price * quantity
        total += product.subtotal
        products.append(product)

    context = {
        "products": products,
        "total": total
    }

    return render(request, "products/cart.html", context)


def checkout(request):
    request.session["cart"] = {}
    request.session.modified = True

    return render(request, "products/payment_success.html")
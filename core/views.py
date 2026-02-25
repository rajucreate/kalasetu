from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from functools import wraps
from products.models import Product
from accounts.models import User, Role


def landing_page(request):
    latest_products = Product.objects.filter(
        is_approved=True
    ).order_by("-created_at")[:3]

    context = {
        "latest_products": latest_products,
    }

    return render(request, "core/landing.html", context)


def role_required(*roles):
    """
    Decorator to restrict access to views based on user role.
    Usage: @role_required(Role.ADMIN, Role.ARTISAN)
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You don't have permission to access this page.")
                return redirect("landing_page")
        return wrapper
    return decorator


@role_required(Role.ADMIN)
def admin_dashboard(request):
    """
    Admin Dashboard with comprehensive statistics and ORM aggregation.
    
    Displays:
    - Total users (overall and by role)
    - Product statistics (total, approved, pending)
    - Recent activity (users and products in last 7 days)
    - Product pricing statistics
    """
    
    # === USER STATISTICS ===
    total_users = User.objects.count()
    
    # Users count by role using aggregation
    users_by_role = User.objects.values('role').annotate(count=Count('id')).order_by('role')
    role_breakdown = {item['role']: item['count'] for item in users_by_role}
    
    # Recent users (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_users_count = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    # === PRODUCT STATISTICS ===
    # Basic product counts
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products = Product.objects.filter(is_approved=False).count()
    
    # Product approval rate (percentage)
    approval_rate = (approved_products / total_products * 100) if total_products > 0 else 0
    
    # Recent products (last 7 days)
    recent_products_count = Product.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Products lists for moderation tables
    pending_products_list = Product.objects.filter(
        is_approved=False
    ).select_related('artisan').order_by('-created_at')
    approved_products_list = Product.objects.filter(
        is_approved=True
    ).select_related('artisan').order_by('-created_at')
    
    # === ARTISAN STATISTICS ===
    # Top artisans by product count
    top_artisans = User.objects.filter(
        role=Role.ARTISAN
    ).annotate(
        product_count=Count('products'),
        approved_count=Count('products', filter=Q(products__is_approved=True))
    ).order_by('-product_count')[:5]
    
    # === PRODUCT PRICING STATISTICS ===
    # Aggregate pricing data
    pricing_stats = Product.objects.aggregate(
        avg_price=Avg('price'),
        total_value=Sum('price', filter=Q(is_approved=True))
    )
    
    # Build context dictionary
    context = {
        # User statistics
        'total_users': total_users,
        'role_breakdown': role_breakdown,
        'admin_count': role_breakdown.get(Role.ADMIN, 0),
        'artisan_count': role_breakdown.get(Role.ARTISAN, 0),
        'buyer_count': role_breakdown.get(Role.BUYER, 0),
        'consultant_count': role_breakdown.get(Role.CONSULTANT, 0),
        'recent_users_count': recent_users_count,
        
        # Product statistics
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'approval_rate': round(approval_rate, 1),
        'recent_products_count': recent_products_count,
        
        # Product details
        'pending_products_list': pending_products_list,
        'approved_products_list': approved_products_list,
        'top_artisans': top_artisans,
        
        # Pricing statistics
        'average_price': pricing_stats['avg_price'] or 0,
        'total_marketplace_value': pricing_stats['total_value'] or 0,
        
        # Current admin user
        'admin_user': request.user,
    }

    return render(request, "dashboards/admin_dashboard.html", context)


@role_required(Role.ADMIN)
@require_POST
def approve_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_approved=False)
    product.is_approved = True
    product.save(update_fields=["is_approved"])
    messages.success(request, f"Approved product: {product.name}")
    return redirect("admin_dashboard")


@role_required(Role.ADMIN)
@require_POST
def reject_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_approved=False)
    product_name = product.name
    product.delete()
    messages.warning(request, f"Rejected and removed product: {product_name}")
    return redirect("admin_dashboard")


@role_required(Role.ARTISAN)
def artisan_dashboard(request):
    artisan_products = Product.objects.filter(
        artisan=request.user
    ).order_by("-created_at")

    total_products = artisan_products.count()
    approved_products = artisan_products.filter(is_approved=True).count()
    pending_products = artisan_products.filter(is_approved=False).count()

    context = {
        "artisan_products": artisan_products,
        "total_products": total_products,
        "approved_products": approved_products,
        "pending_products": pending_products,
    }

    return render(request, "dashboards/artisan_dashboard.html", context)


@role_required(Role.BUYER)
def buyer_dashboard(request):
    cart = request.session.get("cart", {})
    cart_item_count = sum(cart.values()) if cart else 0

    latest_products = Product.objects.filter(
        is_approved=True
    ).select_related("artisan").order_by("-created_at")[:3]

    context = {
        "cart_item_count": cart_item_count,
        "latest_products": latest_products,
    }

    return render(request, "dashboards/buyer_dashboard.html", context)


@role_required(Role.CONSULTANT)
def consultant_dashboard(request):
    return render(request, "dashboards/consultant_dashboard.html")
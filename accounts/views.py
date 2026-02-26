from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegisterForm, ArtisanStoryForm
from .models import Role, User, ArtisanStory
from core.views import role_required
from products.models import Product


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login with email-based authentication and role-based redirects.
    
    GET: Display login form
    POST: Authenticate user and redirect to role-specific dashboard
    """
    # Redirect already authenticated users to their dashboard
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request)
    
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        
        # Get credentials from POST data
        email = request.POST.get("username") or request.POST.get("email")
        password = request.POST.get("password")
        
        # Validate that both fields are provided
        if not email or not password:
            messages.error(request, "Please provide both email and password.")
            return render(request, "accounts/login.html", {"form": form})
        
        # Authenticate user with email
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Check if user account is active
            if not user.is_active:
                messages.error(request, "Your account has been disabled.")
                return render(request, "accounts/login.html", {"form": form})
            
            # Log the user in
            login(request, user)
            messages.success(request, f"Welcome back, {user.email}!")
            
            # Get next parameter for redirect, or use role-based redirect
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            
            # Role-based redirect
            return redirect_user_based_on_role(request)
        else:
            # Authentication failed
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, "accounts/login.html", {"form": form})
    
    # GET request - show login form
    form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def redirect_user_based_on_role(request):
    """
    Redirect authenticated user to their role-specific dashboard.
    
    Args:
        request: HttpRequest object with authenticated user
        
    Returns:
        HttpResponseRedirect to the appropriate dashboard
    """
    role_redirects = {
        Role.ADMIN: "admin_dashboard",
        Role.ARTISAN: "artisan_dashboard",
        Role.BUYER: "buyer_dashboard",
        Role.CONSULTANT: "consultant_dashboard",
    }
    
    # Get the redirect URL name for the user's role
    redirect_name = role_redirects.get(request.user.role)
    
    if redirect_name:
        return redirect(redirect_name)
    else:
        # Fallback if role is not recognized
        messages.warning(request, "Your role is not recognized. Please contact support.")
        return redirect("landing_page")


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Handle user logout.
    
    Logs out the user, clears session data, and redirects to landing page.
    """
    user_email = request.user.email if request.user.is_authenticated else None
    
    # Log the user out
    logout(request)
    
    # Success message
    if user_email:
        messages.success(request, f"You have been logged out successfully. Goodbye!")
    
    # Redirect to landing page
    return redirect("landing_page")


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("landing_page")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect("login")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def artisan_profile(request, pk):
    artisan = get_object_or_404(User, pk=pk, role=Role.ARTISAN)
    artisan_products = Product.objects.filter(
        artisan=artisan,
        is_approved=True
    ).order_by("-created_at")

    stories = ArtisanStory.objects.filter(
        artisan=artisan
    ).order_by("-created_at")

    verified_products = artisan_products.filter(
        verification_status=Product.VerificationStatus.VERIFIED
    ).count()
    total_products = artisan_products.count()

    # Basic impact metric for public display.
    impact_score = verified_products * 10

    context = {
        "artisan": artisan,
        "products": artisan_products,
        "stories": stories,
        "total_products": total_products,
        "verified_products": verified_products,
        "impact_score": impact_score,
    }

    return render(request, "accounts/artisan_profile.html", context)


@role_required(Role.ARTISAN)
def add_story(request):
    if request.method == "POST":
        form = ArtisanStoryForm(request.POST, request.FILES)
        if form.is_valid():
            # Attach the story to the logged-in artisan.
            story = form.save(commit=False)
            story.artisan = request.user
            story.save()
            messages.success(request, "Story added to your public profile.")
            return redirect("artisan_dashboard")
        messages.error(request, "Please fix the errors below.")
    else:
        form = ArtisanStoryForm()

    return render(request, "accounts/add_story.html", {"form": form})
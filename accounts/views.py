from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegisterForm
from .models import Role


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
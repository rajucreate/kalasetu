"""
Role-based permission classes for API endpoints.
Controls access based on user role: ADMIN, ARTISAN, BUYER, CONSULTANT.
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to Admin users."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == 'ADMIN')


class IsArtisan(permissions.BasePermission):
    """Allow access only to Artisan users."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == 'ARTISAN')


class IsConsultant(permissions.BasePermission):
    """Allow access only to Consultant users."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == 'CONSULTANT')


class IsBuyer(permissions.BasePermission):
    """Allow access only to Buyer users."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == 'BUYER')


class IsArtisanOwner(permissions.BasePermission):
    """Allow access only if user is the owner artisan of the product."""
    
    def has_object_permission(self, request, view, obj):
        return obj.artisan == request.user


class IsConsultantOrAdmin(permissions.BasePermission):
    """Allow access to Consultants or Admins."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in ['CONSULTANT', 'ADMIN'])


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit, others to read only."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # For product/story models, ownership is through `artisan` relation.
        if hasattr(obj, 'artisan'):
            return obj.artisan == request.user

        return False

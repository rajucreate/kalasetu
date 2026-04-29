"""
API Views for REST endpoints.
Provides views for authentication, products, artisans, stories, and consultant operations.
"""

from rest_framework import status, viewsets, views, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from decimal import Decimal, InvalidOperation
import json
from urllib import parse, request as urllib_request
from urllib.error import URLError, HTTPError

from products.models import Product
from accounts.models import ArtisanStory

from .serializers import (
    UserRegisterSerializer, UserDetailSerializer, UserPublicSerializer,
    ArtisanProfileSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductWriteSerializer, ProductVerificationSerializer,
    ArtisanStoryListSerializer, ArtisanStoryDetailSerializer, ArtisanStoryWriteSerializer
)
from .permissions import (
    IsAdmin, IsArtisan, IsConsultantOrAdmin, IsArtisanOwner, IsOwnerOrReadOnly
)

User = get_user_model()




def _verify_captcha_token(captcha_token):
    """Validate Google reCAPTCHA token using secret key from environment."""
    if not captcha_token:
        return False, 'Captcha is required.'

    secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    if not secret_key:
        return False, 'Captcha is not configured on the server.'

    payload = parse.urlencode({
        'secret': secret_key,
        'response': captcha_token,
    }).encode('utf-8')

    verify_request = urllib_request.Request(
        'https://www.google.com/recaptcha/api/siteverify',
        data=payload,
        method='POST',
    )

    try:
        with urllib_request.urlopen(verify_request, timeout=8) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (URLError, HTTPError, TimeoutError, ValueError):
        return False, 'Captcha verification failed. Please try again.'

    if result.get('success'):
        return True, None

    return False, 'Captcha validation failed. Please try again.'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customize token response to include user data."""
    captcha_token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        captcha_token = attrs.pop('captcha_token', None)
        is_valid, error_message = _verify_captcha_token(captcha_token)
        if not is_valid:
            raise serializers.ValidationError({'detail': error_message})

        return super().validate(attrs)
    
    def get_token(self, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        token['email'] = user.email
        return token
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Token obtain view with custom serializer."""
    serializer_class = CustomTokenObtainPairSerializer


# ============== AUTH ENDPOINTS ==============

class RegisterView(views.APIView):
    """Register a new user."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        is_valid_captcha, captcha_error = _verify_captcha_token(request.data.get('captcha_token'))
        if not is_valid_captcha:
            return Response({'detail': captcha_error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'email': user.email,
                'role': user.role,
                'message': 'User registered successfully. Please login.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============== USER ENDPOINTS ==============

class CurrentUserView(views.APIView):
    """Get or update current logged-in user profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user profile."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user profile."""
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============== PRODUCT ENDPOINTS ==============

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.
    - GET /api/products/ : List all verified products
    - GET /api/products/<id>/ : Product detail
    - POST /api/products/ : Create product (Artisans only)
    - PUT/PATCH /api/products/<id>/ : Update product (Owner only)
    """
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        if self.action == 'verify':
            return ProductVerificationSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsArtisan()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsArtisanOwner()]
        elif self.action in ['pending_approval', 'approve', 'reject']:
            return [IsAuthenticated(), IsAdmin()]
        return [AllowAny()]
    
    def get_queryset(self):
        """
        Filter products based on user role:
        - Public users: Only verified products
        - Artisans: Their own products + verified products
        - Admins/Consultants: All products
        """
        user = self.request.user
        params = self.request.query_params

        queryset = Product.objects.select_related('artisan', 'verified_by').all()
        
        if user.is_authenticated:
            if user.role in ['ADMIN', 'CONSULTANT']:
                queryset = queryset
            elif user.role == 'ARTISAN':
                # Show own products + verified products
                queryset = queryset.filter(
                    Q(artisan=user) |
                    Q(is_approved=True, verification_status=Product.VerificationStatus.VERIFIED)
                )
            else:
                queryset = queryset.filter(is_approved=True).exclude(
                    verification_status=Product.VerificationStatus.REJECTED
                )
        else:
            queryset = queryset.filter(is_approved=True).exclude(
                verification_status=Product.VerificationStatus.REJECTED
            )

        search = params.get('search')
        region = params.get('region')
        verification_status = params.get('verification_status')
        is_verified = params.get('is_verified')
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        ordering = params.get('ordering', '-created_at')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(cultural_story__icontains=search)
            )

        if region:
            queryset = queryset.filter(region__icontains=region)

        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)

        if is_verified is not None:
            normalized = str(is_verified).lower()
            if normalized in ['true', '1', 'yes']:
                queryset = queryset.filter(is_verified=True)
            elif normalized in ['false', '0', 'no']:
                queryset = queryset.filter(is_verified=False)

        if min_price is not None:
            try:
                min_price = Decimal(min_price)
            except (InvalidOperation, TypeError):
                raise ValidationError({'min_price': 'min_price must be a valid number.'})
            queryset = queryset.filter(price__gte=min_price)

        if max_price is not None:
            try:
                max_price = Decimal(max_price)
            except (InvalidOperation, TypeError):
                raise ValidationError({'max_price': 'max_price must be a valid number.'})
            queryset = queryset.filter(price__lte=max_price)

        allowed_ordering = {'created_at', '-created_at', 'price', '-price', 'name', '-name'}
        if ordering not in allowed_ordering:
            ordering = '-created_at'

        return queryset.order_by(ordering)
    
    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(artisan=request.user)
            detail_data = ProductDetailSerializer(
                Product.objects.select_related('artisan', 'verified_by').get(id=serializer.instance.id)
            ).data
            return Response(detail_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update own product."""
        product = self.get_object()
        if product.artisan != request.user:
            raise PermissionDenied(detail='You can only edit your own products.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        product = self.get_object()
        if product.artisan != request.user:
            raise PermissionDenied(detail='You can only edit your own products.')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.artisan != request.user:
            raise PermissionDenied(detail='You can only delete your own products.')
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'], 
            permission_classes=[IsAuthenticated, IsConsultantOrAdmin])
    def verify(self, request, pk=None):
        """
        Verify a product (Consultant/Admin only).
        PATCH /api/products/<id>/verify/
        """
        product = self.get_object()
        serializer = ProductVerificationSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(verified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsConsultantOrAdmin])
    def pending(self, request):
        """Get pending verification products (Consultant only)."""
        products = Product.objects.filter(
            verification_status=Product.VerificationStatus.PENDING
        ).select_related('artisan', 'verified_by').order_by('-created_at')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsArtisan])
    def my_products(self, request):
        """Get current user's products (Artisan only)."""
        products = Product.objects.filter(artisan=request.user).order_by('-created_at')
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdmin])
    def pending_approval(self, request):
        """Get products waiting for admin approval."""
        products = Product.objects.filter(is_approved=False).exclude(
            verification_status=Product.VerificationStatus.REJECTED
        ).select_related('artisan', 'verified_by').order_by('-created_at')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdmin])
    def approve(self, request, pk=None):
        """Approve product for marketplace visibility (Admin only)."""
        product = self.get_object()
        product.is_approved = True

        # If previously rejected, reset to pending for consultant review.
        if product.verification_status == Product.VerificationStatus.REJECTED:
            product.verification_status = Product.VerificationStatus.PENDING
            product.is_verified = False

        product.save(update_fields=['is_approved', 'verification_status', 'is_verified'])
        return Response({'message': 'Product approved successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdmin])
    def reject(self, request, pk=None):
        """Reject product and remove from marketplace (Admin only)."""
        product = self.get_object()
        product.is_approved = False
        product.is_verified = False
        product.verification_status = Product.VerificationStatus.REJECTED
        product.save(update_fields=['is_approved', 'is_verified', 'verification_status'])
        return Response({'message': 'Product rejected and removed from marketplace.'}, status=status.HTTP_200_OK)


# ============== ARTISAN ENDPOINTS ==============

class ArtisanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for artisans (read-only).
    - GET /api/artisans/ : List all artisans
    - GET /api/artisans/<id>/ : Artisan detail
    """
    queryset = User.objects.filter(role='ARTISAN').prefetch_related('products', 'stories')
    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArtisanProfileSerializer
        return UserPublicSerializer


# ============== ARTISAN STORY ENDPOINTS ==============

class ArtisanStoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for artisan stories.
    - GET /api/stories/ : List all stories
    - GET /api/stories/<id>/ : Story detail
    - POST /api/stories/ : Create story (Artisan only)
    - PUT/PATCH /api/stories/<id>/ : Update story (Owner only)
    """
    serializer_class = ArtisanStoryListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArtisanStoryDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ArtisanStoryWriteSerializer
        return ArtisanStoryListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsArtisan()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Return all stories (public content)."""
        return ArtisanStory.objects.select_related('artisan').all().order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new story."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(artisan=request.user)
            detail_data = ArtisanStoryDetailSerializer(
                ArtisanStory.objects.select_related('artisan').get(id=serializer.instance.id)
            ).data
            return Response(detail_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        story = self.get_object()
        if story.artisan != request.user:
            raise PermissionDenied(detail='You can only edit your own stories.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        story = self.get_object()
        if story.artisan != request.user:
            raise PermissionDenied(detail='You can only edit your own stories.')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        story = self.get_object()
        if story.artisan != request.user:
            raise PermissionDenied(detail='You can only delete your own stories.')
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsArtisan])
    def my_stories(self, request):
        """Get current user's stories (Artisan only)."""
        stories = ArtisanStory.objects.filter(artisan=request.user).order_by('-created_at')
        page = self.paginate_queryset(stories)
        if page is not None:
            serializer = ArtisanStoryListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ArtisanStoryListSerializer(stories, many=True, context={'request': request})
        return Response(serializer.data)


# ============== CONSULTANT ENDPOINTS ==============

class ConsultantPendingView(views.APIView):
    """Get pending products for consultant review."""
    permission_classes = [IsAuthenticated, IsConsultantOrAdmin]
    
    def get(self, request):
        """GET /api/consultant/pending/"""
        products = Product.objects.filter(
            verification_status=Product.VerificationStatus.PENDING
        ).select_related('artisan', 'verified_by').order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ConsultantVerifyView(views.APIView):
    """Verify or reject a product."""
    permission_classes = [IsAuthenticated, IsConsultantOrAdmin]
    
    def patch(self, request, product_id):
        """PATCH /api/consultant/verify/<id>/"""
        try:
            product = Product.objects.select_related('artisan', 'verified_by').get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound(detail='Product not found.')
        
        serializer = ProductVerificationSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(verified_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

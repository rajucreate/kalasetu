"""
API Serializers for REST endpoints.
Handles data serialization/deserialization for User, Product, ArtisanStory, etc.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from products.models import Product
from accounts.models import ArtisanStory

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Limited public view of user profile - for artisan listings."""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'bio', 
                  'region', 'experience_years', 'profile_image')
        read_only_fields = ('id', 'role')


class UserDetailSerializer(serializers.ModelSerializer):
    """Full user profile with all fields."""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone_number',
                  'bio', 'region', 'experience_years', 'profile_image')
        read_only_fields = ('id', 'role')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 
                  'role', 'phone_number', 'region')
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        return data
    
    def create(self, validated_data):
        """Create user with password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ArtisanStoryListSerializer(serializers.ModelSerializer):
    """Serializer for story list view."""
    artisan = UserPublicSerializer(read_only=True)

    class Meta:
        model = ArtisanStory
        fields = ('id', 'title', 'image', 'created_at', 'artisan')
        read_only_fields = ('id', 'created_at', 'artisan')


class ArtisanStoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for story detail view."""
    artisan = UserPublicSerializer(read_only=True)

    class Meta:
        model = ArtisanStory
        fields = ('id', 'title', 'content', 'image', 'created_at', 'artisan')
        read_only_fields = ('id', 'created_at', 'artisan')


class ArtisanStoryWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating own stories."""

    class Meta:
        model = ArtisanStory
        fields = ('title', 'content', 'image')


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view - minimal fields."""
    artisan = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'region', 'artisan',
                  'is_approved', 'verification_status', 'verification_note', 'is_verified', 'created_at')
        read_only_fields = (
            'id',
            'created_at',
            'is_approved',
            'verification_status',
            'verification_note',
            'is_verified',
        )


class ArtisanProfileSerializer(serializers.ModelSerializer):
    """Public artisan profile with featured approved products."""
    products = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'bio',
                  'region', 'experience_years', 'profile_image', 'phone_number', 'products')
        read_only_fields = fields

    def get_products(self, obj):
        products = obj.products.exclude(
            verification_status=Product.VerificationStatus.REJECTED
        ).order_by('-created_at')
        return ProductListSerializer(products, many=True, context=self.context).data


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail view - all fields."""
    artisan = UserPublicSerializer(read_only=True)
    verified_by = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'region', 
                  'cultural_story', 'craft_process', 'artisan',
                  'is_approved', 'verification_status', 'is_verified', 
                  'verified_by', 'verification_note', 'impact_score', 'created_at')
        read_only_fields = ('id', 'created_at', 'verification_status', 'is_verified', 
                           'verified_by', 'verification_note', 'verified_at', 'impact_score')


class ProductWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products by artisans."""

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image', 'region', 'cultural_story', 'craft_process')


class ProductVerificationSerializer(serializers.ModelSerializer):
    """Serializer for consultant to verify products."""
    
    class Meta:
        model = Product
        fields = ('verification_status', 'verification_note', 'impact_score')
    
    def validate_verification_status(self, value):
        """Only allow VERIFIED or REJECTED."""
        if value not in [Product.VerificationStatus.VERIFIED, Product.VerificationStatus.REJECTED]:
            raise serializers.ValidationError(
                "Verification status must be VERIFIED or REJECTED."
            )
        return value

    def validate_impact_score(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Impact score must be between 0 and 100.")
        return value

    def update(self, instance, validated_data):
        """Auto-sync is_approved and is_verified with the consultant's decision."""
        from django.utils import timezone
        v_status = validated_data.get('verification_status', instance.verification_status)
        if v_status == Product.VerificationStatus.VERIFIED:
            instance.is_approved = True
            instance.is_verified = True
            instance.verified_at = timezone.now()
        elif v_status == Product.VerificationStatus.REJECTED:
            instance.is_approved = False
            instance.is_verified = False
            instance.verified_at = timezone.now()
        instance.verification_status = v_status
        instance.verification_note = validated_data.get('verification_note', instance.verification_note)
        instance.impact_score = validated_data.get('impact_score', instance.impact_score)
        # verified_by is set by the view via save(verified_by=request.user)
        verified_by = validated_data.get('verified_by', None)
        if verified_by:
            instance.verified_by = verified_by
        instance.save(update_fields=[
            'verification_status', 'verification_note', 'impact_score',
            'is_approved', 'is_verified', 'verified_at',
        ])
        return instance

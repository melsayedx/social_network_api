"""User serializers with phone number support."""
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for public user profile data."""
    
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "bio",
            "avatar",
            "followers_count",
            "following_count",
            "posts_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserDetailSerializer(UserSerializer):
    """Extended serializer for detailed user profile (includes email/phone for owner)."""
    
    email = serializers.EmailField(read_only=True)
    phone_number = PhoneNumberField(read_only=True)
    preferences = serializers.JSONField(read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["email", "phone_number", "preferences"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password", "password_confirm"]
    
    def validate(self, attrs: dict) -> dict:
        """Validate that passwords match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data: dict) -> User:
        """Create new user with hashed password (uses Argon2)."""
        validated_data.pop("password_confirm")
        phone_number = validated_data.pop("phone_number", None)
        
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        
        if phone_number:
            user.phone_number = phone_number
            user.save(update_fields=["phone_number"])
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ["bio", "avatar", "phone_number", "preferences"]
    
    def validate_preferences(self, value: dict) -> dict:
        """Validate preferences structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferences must be a JSON object.")
        
        # Merge with existing preferences instead of replacing
        if self.instance:
            existing = self.instance.preferences or {}
            existing.update(value)
            return existing
        return value

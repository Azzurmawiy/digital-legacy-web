from rest_framework import serializers
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):
    """Serializer for managing beneficiaries."""
    
    class Meta:
        model = Beneficiary
        fields = ['id', 'name', 'email', 'relationship', 'permissions', 'verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'verified', 'created_at', 'updated_at']

    def validate_email(self, value):
        user = self.context['request'].user
        if user.email == value:
            raise serializers.ValidationError("You cannot add yourself as a beneficiary.")
        
        # Check if beneficiary already exists for this user (for create or update if email changed)
        if self.instance is None or self.instance.email != value:
            if Beneficiary.objects.filter(user=user, email=value).exists():
                raise serializers.ValidationError("A beneficiary with this email already exists.")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Beneficiary.objects.create(user=user, **validated_data)

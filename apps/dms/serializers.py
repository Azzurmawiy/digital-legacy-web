from rest_framework import serializers
from .models import DMSConfig, Heartbeat


class DMSConfigSerializer(serializers.ModelSerializer):
    """Serializer for Dead Man's Switch configuration."""
    
    class Meta:
        model = DMSConfig
        fields = [
            'id', 'inactivity_threshold_days', 'cooling_off_days', 
            'status', 'last_triggered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'last_triggered', 'created_at', 'updated_at']

    def validate_inactivity_threshold_days(self, value):
        if value < 7:
            raise serializers.ValidationError("Inactivity threshold must be at least 7 days.")
        return value

    def validate_cooling_off_days(self, value):
        if value < 1:
            raise serializers.ValidationError("Cooling off period must be at least 1 day.")
        return value


class HeartbeatSerializer(serializers.ModelSerializer):
    """Serializer for receiving heartbeat signals."""
    
    class Meta:
        model = Heartbeat
        fields = ['id', 'source', 'timestamp', 'ip_hash']
        read_only_fields = ['id', 'timestamp', 'ip_hash']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        
        # Get IP Hash from request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        ip = ip or '0.0.0.0'
        import hashlib
        ip_hash = hashlib.sha256(ip.encode('utf-8')).hexdigest()
        
        # Create heartbeat
        heartbeat = Heartbeat.objects.create(
            user=user,
            ip_hash=ip_hash,
            **validated_data
        )
        
        # Update user's last_active_at and reset DMS config if active/warning
        user.update_last_active()
        
        # Reset DMS status if it was in warning phase
        try:
            dms = user.dms_config
            if dms.status in [DMSConfig.Status.WARNING_1, DMSConfig.Status.WARNING_2, DMSConfig.Status.COOLING_OFF]:
                dms.status = DMSConfig.Status.ACTIVE
                dms.save(update_fields=['status'])
        except DMSConfig.DoesNotExist:
            pass
            
        return heartbeat

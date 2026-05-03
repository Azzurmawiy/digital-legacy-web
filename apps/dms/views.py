from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DMSConfig, Heartbeat
from .serializers import DMSConfigSerializer, HeartbeatSerializer


class DMSConfigView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the user's Dead Man's Switch configuration.
    Creates a default configuration if one does not exist.
    """
    serializer_class = DMSConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, created = DMSConfig.objects.get_or_create(user=self.request.user)
        return obj


class HeartbeatCreateView(generics.CreateAPIView):
    """
    Record a heartbeat signal to prove the user is active.
    This also resets any active DMS warnings and updates the user's last_active_at timestamp.
    """
    serializer_class = HeartbeatSerializer
    permission_classes = [IsAuthenticated]


class DMSCancelView(views.APIView):
    """
    Cancel an active cooling-off period and reset the DMS status back to ACTIVE.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            dms_config = request.user.dms_config
        except DMSConfig.DoesNotExist:
            return Response(
                {"error": "DMS configuration not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if dms_config.status not in [DMSConfig.Status.WARNING_1, DMSConfig.Status.WARNING_2, DMSConfig.Status.COOLING_OFF]:
            return Response(
                {"message": "DMS is not currently triggered or in warning state."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status
        dms_config.status = DMSConfig.Status.ACTIVE
        dms_config.save(update_fields=['status'])
        
        # Also record a heartbeat automatically
        request.user.update_last_active()

        return Response({"message": "DMS cancelled successfully. Status is now ACTIVE."})

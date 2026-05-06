from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Beneficiary
from .serializers import BeneficiarySerializer


class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for user's beneficiaries.
    Only allows users to manage their own beneficiaries.
    """
    serializer_class = BeneficiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only view and manage their own beneficiaries
        return Beneficiary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        beneficiary = serializer.save()
        
        # Send live email notification to the beneficiary
        from apps.notifications.tasks import send_email_notification
        user = self.request.user
        send_email_notification.delay(
            user.id,
            subject="Digital Legacy Designation",
            message=f"Hello {beneficiary.name},\n\nYou have been designated as a beneficiary by {user.full_name} on the Digital Legacy platform.",
            recipient_email=beneficiary.email
        )

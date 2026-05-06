from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
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

    def destroy(self, request, *args, **kwargs):
        """
        Delete a beneficiary. Idempotent: returns 204 even if beneficiary doesn't exist.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            # Beneficiary doesn't exist, but DELETE is idempotent
            return Response(status=status.HTTP_204_NO_CONTENT)

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

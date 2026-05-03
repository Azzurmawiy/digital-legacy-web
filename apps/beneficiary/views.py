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

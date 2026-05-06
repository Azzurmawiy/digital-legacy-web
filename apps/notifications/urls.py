from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

app_name = 'notifications'

class NotificationHistoryView(APIView):
    """
    Retrieve the user's notification history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import Notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        data = [{
            "id": n.id,
            "action": n.subject or "System Event",
            "detail": n.message,
            "time": n.created_at.isoformat(),
            "status": n.status,
            "channel": n.channel,
            "icon": "ShieldCheck" if "Vault" in (n.subject or "") else "Activity"
        } for n in notifications[:50]]
        return Response({
            "success": True,
            "data": data
        })


urlpatterns = [
    path('history/', NotificationHistoryView.as_view(), name='history'),
]

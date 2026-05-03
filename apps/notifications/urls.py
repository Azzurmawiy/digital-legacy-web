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
            "channel": n.channel,
            "subject": n.subject,
            "status": n.status,
            "created_at": n.created_at
        } for n in notifications[:50]]
        return Response(data)


urlpatterns = [
    path('history/', NotificationHistoryView.as_view(), name='history'),
]

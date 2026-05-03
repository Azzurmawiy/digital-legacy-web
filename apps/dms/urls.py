from django.urls import path
from . import views

app_name = 'dms'

urlpatterns = [
    path('config/', views.DMSConfigView.as_view(), name='config'),
    path('heartbeat/', views.HeartbeatCreateView.as_view(), name='heartbeat'),
    path('cancel/', views.DMSCancelView.as_view(), name='cancel'),
]

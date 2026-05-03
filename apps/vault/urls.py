# apps/vault/urls.py
from django.urls import path
from .views import VaultListView, VaultUploadView, VaultDownloadView, VaultDestroyView, VaultUpdateView

app_name = 'vault'

urlpatterns = [
    # TODO: Add vault endpoints
    path('items/', VaultListView.as_view(), name='vault-list'),
    path('items/<uuid:pk>/', VaultUpdateView.as_view(), name='vault-update'),
    path('items/<uuid:pk>/delete/', VaultDestroyView.as_view(), name='vault-delete'),
    path('upload/', VaultUploadView.as_view(), name='vault-upload'),
    path('<uuid:pk>/download/', VaultDownloadView.as_view(), name='vault-download'),
]
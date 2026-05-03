from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'beneficiary'

router = DefaultRouter()
router.register(r'', views.BeneficiaryViewSet, basename='beneficiary')

urlpatterns = [
    path('', include(router.urls)),
]
